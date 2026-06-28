"""Enterprise Context Engine — Core Orchestrator.

Orchestrates the assembly of EnterpriseContext using the dependency graph,
provider registry, validation gate, ranker, compressor, and window builder.

Never accesses databases or providers directly.
"""

import asyncio
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

import structlog

from app.core.context import OperationContext
from app.models.enterprise_context import (
    ContextMetadata,
    ContextSection,
    ContextWindow,
    EnterpriseContext,
    EnterpriseContextCreate,
    ProviderFailureRecord,
    ContextLifecycleCreate,
    ContextLifecycleUpdate,
)
from app.models.enums import ContextStatus, ContextSource
from app.models.events import (
    ContextBuiltEvent, 
    ContextPartiallyBuiltEvent,
    ContextCompressedEvent,
    ContextWindowCreatedEvent,
)
from app.models.exceptions import (
    ContextAssemblyError,
    ContextValidationError,
)
from app.services.context_policies import BUILT_IN_POLICIES
from app.services.context_retry import provide_with_retry
from app.repositories.enterprise_context_repository import AbstractEnterpriseContextRepository

logger = structlog.get_logger(__name__)


class AbstractContextEngine(ABC):
    @abstractmethod
    async def build(
        self,
        ctx: OperationContext,
        command: EnterpriseContextCreate,
    ) -> EnterpriseContext:
        """Assemble an EnterpriseContext according to the requested policy."""
        pass


class ContextEngine(AbstractContextEngine):
    """Core orchestrator for EnterpriseContext assembly."""

    def __init__(
        self,
        provider_registry,          # ContextProviderRegistry
        dependency_graph,           # ContextDependencyGraph
        validator,                  # AbstractContextValidator
        ranker,                     # AbstractContextRanker
        compressor,                 # AbstractContextCompressor
        window_builder,             # AbstractContextWindowBuilder
        repository: AbstractEnterpriseContextRepository = None,
        event_bus=None,             # EventBus
        trace_service=None,         # AbstractCognitiveTraceService
    ) -> None:
        self._registry = provider_registry
        self._graph = dependency_graph
        self._validator = validator
        self._ranker = ranker
        self._compressor = compressor
        self._window_builder = window_builder
        self._repository = repository
        self._event_bus = event_bus
        self._trace_service = trace_service

    async def build(
        self,
        ctx: OperationContext,
        command: EnterpriseContextCreate,
    ) -> EnterpriseContext:
        log = ctx.bind_to_logger(logger).bind(policy_id=command.policy_id)
        start_time = time.perf_counter()

        # 1. Initialization
        policy = BUILT_IN_POLICIES.get(command.policy_id)
        if not policy:
            raise ContextAssemblyError(f"Unknown context policy: {command.policy_id}")

        context_id = uuid4()
        
        # Persist BUILDING lifecycle
        if self._repository:
            await self._repository.create(
                ContextLifecycleCreate(
                    context_id=context_id,
                    twin_id=command.twin_id,
                    policy_id=policy.policy_id,
                    schema_version="1.0"
                )
            )

        execution_plan = self._graph.resolve(policy.enabled_providers)

        # 2. Execute Providers
        sections, failures, provider_latencies = await self._execute_providers(
            ctx, command, policy, execution_plan
        )
        
        # Check Required Providers
        failed_sources = {f.provider for f in failures}
        missing_required = failed_sources.intersection(policy.required_providers)
        if missing_required:
            missing_names = ", ".join(s.value for s in missing_required)
            raise ContextAssemblyError(f"Required providers failed: {missing_names}")

        # Update lifecycle to ASSEMBLED
        if self._repository:
            await self._repository.update_status(
                context_id, 
                ContextLifecycleUpdate(status=ContextStatus.ASSEMBLED)
            )

        # 3. Validate
        self._validate(sections, policy)

        # 4. Rank
        ranked_sections, rank_latency = self._rank(sections, policy)

        # 5. Compress
        compressed_sections, comp_latency, comp_ratio, token_before, token_after, items_before, items_after = self._compress(
            ranked_sections, policy, ctx, context_id, command
        )

        # 6. Build Window
        window, win_latency = self._build_window(compressed_sections, policy, ctx, context_id, command)
        
        total_latency = (time.perf_counter() - start_time) * 1000

        # 7. Assemble EnterpriseContext
        metadata = ContextMetadata(
            policy_id=policy.policy_id,
            total_providers_requested=execution_plan.total_providers,
            successful_providers=len(sections),
            failed_providers=len(failures),
            missing_providers=failures,
            ranking_latency_ms=rank_latency,
            compression_latency_ms=comp_latency,
            window_latency_ms=win_latency,
            total_assembly_latency_ms=total_latency,
            token_estimate_before_compression=token_before,
            token_estimate_after_compression=token_after,
            compression_ratio=comp_ratio,
            items_total=items_before,
            items_retained=items_after,
            per_provider_latency_ms=provider_latencies,
        )

        context = EnterpriseContext(
            context_id=context_id,
            twin_id=command.twin_id,
            status=ContextStatus.OPTIMIZED,
            sections=window.sections,
            window=window,
            metadata=metadata,
            intent_id=command.intent_id,
            operation_context_id=ctx.request_id,
        )

        # Update lifecycle to OPTIMIZED
        if self._repository:
            await self._repository.update_status(
                context_id, 
                ContextLifecycleUpdate(
                    status=ContextStatus.OPTIMIZED,
                    is_partial=len(failures) > 0
                )
            )

        # 8. Events and Traces
        await self._publish_events(ctx, context, sections, failures, policy, total_latency)
        self._record_trace(ctx, context, total_latency, rank_latency, comp_latency, win_latency, comp_ratio, provider_latencies)

        log.info(
            "EnterpriseContext assembled",
            context_id=str(context.context_id),
            token_estimate=window.token_estimate,
            items_retained=items_after,
            latency_ms=total_latency,
        )
        return context

    async def _execute_providers(
        self, ctx, command, policy, execution_plan
    ) -> Tuple[List[ContextSection], List[ProviderFailureRecord], Dict[str, float]]:
        sections = []
        failures = []
        provider_latencies = {}

        for batch in execution_plan.batches:
            tasks = []
            sources = []
            for source in batch:
                entry = self._registry.get_entry(source)
                tasks.append(
                    self._execute_single_provider(
                        provider=entry.provider,
                        retry_config=entry.retry_config,
                        ctx=ctx,
                        twin_id=command.twin_id,
                        policy=policy,
                        source=source,
                    )
                )
                sources.append(source)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for source, result in zip(sources, results):
                if isinstance(result, tuple):
                    res, latency = result
                    provider_latencies[source.value] = latency
                    if isinstance(res, ProviderFailureRecord):
                        failures.append(res)
                    elif isinstance(res, ContextSection) and not res.is_empty:
                        sections.append(res)
                elif isinstance(result, Exception):
                    logger.error("Unhandled provider exception", exc_info=result)

        return sections, failures, provider_latencies

    async def _execute_single_provider(self, provider, retry_config, ctx, twin_id, policy, source):
        start = time.perf_counter()
        result = await provide_with_retry(
            provider=provider,
            retry_config=retry_config,
            ctx=ctx,
            twin_id=twin_id,
            policy=policy,
            source=source,
            event_bus=self._event_bus,
        )
        latency = (time.perf_counter() - start) * 1000
        return result, latency

    def _validate(self, sections, policy):
        validation_result = self._validator.validate(sections, policy)
        if not validation_result.is_valid:
            raise ContextValidationError(validation_result.errors)

    def _rank(self, sections, policy) -> Tuple[List[ContextSection], float]:
        start = time.perf_counter()
        ranked = self._ranker.rank(sections, policy)
        latency = (time.perf_counter() - start) * 1000
        return ranked, latency

    def _compress(self, sections, policy, ctx, context_id, command) -> Tuple[List[ContextSection], float, float, int, int, int, int]:
        start = time.perf_counter()
        token_before = sum(s.token_estimate for s in sections)
        items_before = sum(s.item_count for s in sections)

        compressed = self._compressor.compress(sections, policy.token_budget)

        token_after = sum(s.token_estimate for s in compressed)
        items_after = sum(s.item_count for s in compressed)
        latency = (time.perf_counter() - start) * 1000
        comp_ratio = (items_after / items_before) if items_before > 0 else 1.0

        if self._event_bus:
            self._event_bus.publish(
                ContextCompressedEvent(
                    correlation_id=ctx.correlation_id,
                    context_id=context_id,
                    twin_id=command.twin_id,
                    items_before=items_before,
                    items_after=items_after,
                    compression_ratio=comp_ratio,
                )
            )
            
        return compressed, latency, comp_ratio, token_before, token_after, items_before, items_after

    def _build_window(self, sections, policy, ctx, context_id, command) -> Tuple[ContextWindow, float]:
        start = time.perf_counter()
        # Extract critical reserve from policy dynamically
        critical_reserve = getattr(policy, "critical_reserve", 0.1)
        window = self._window_builder.build_window(sections, policy.token_budget, critical_reserve=critical_reserve)
        latency = (time.perf_counter() - start) * 1000

        if self._event_bus:
            self._event_bus.publish(
                ContextWindowCreatedEvent(
                    correlation_id=ctx.correlation_id,
                    context_id=context_id,
                    twin_id=command.twin_id,
                    token_estimate=window.token_estimate,
                    items_included=window.items_included,
                    overflow=window.overflow,
                )
            )
            
        return window, latency

    async def _publish_events(self, ctx, context, sections, failures, policy, total_latency):
        if not self._event_bus:
            return
            
        if failures:
            self._event_bus.publish(
                ContextPartiallyBuiltEvent(
                    correlation_id=ctx.correlation_id,
                    context_id=context.context_id,
                    twin_id=context.twin_id,
                    successful_providers=[s.source.value for s in sections],
                    failed_providers=[f.provider.value for f in failures],
                    is_usable=True,
                )
            )
        else:
            self._event_bus.publish(
                ContextBuiltEvent(
                    correlation_id=ctx.correlation_id,
                    context_id=context.context_id,
                    twin_id=context.twin_id,
                    policy_id=policy.policy_id,
                    source_count=len(sections),
                    token_estimate=context.window.token_estimate,
                    assembly_latency_ms=total_latency,
                )
            )

    def _record_trace(self, ctx, context, total_latency, rank_latency, comp_latency, win_latency, comp_ratio, provider_latencies):
        if not self._trace_service:
            return
            
        try:
            from app.models.cognitive_trace import CognitiveTraceCreate, CognitiveTraceTokenUsage
            trace = CognitiveTraceCreate(
                twin_id=context.twin_id,
                operation_type="enterprise_context_build",
                prompt_version="n/a",
                provider_model="n/a",
                latency_ms=total_latency,
                token_usage=CognitiveTraceTokenUsage(
                    prompt_tokens=0,
                    completion_tokens=context.window.token_estimate,
                    total_tokens=context.window.token_estimate,
                ),
                context_id=context.context_id,
                context_sources_used=[s.source.value for s in context.sections],
                compression_ratio=comp_ratio,
                ranking_latency_ms=rank_latency,
                compression_latency_ms=comp_latency,
                window_latency_ms=win_latency,
                token_estimate=context.window.token_estimate,
                per_provider_latency_ms=provider_latencies,
            )
            asyncio.create_task(self._trace_service.record_trace(ctx, trace))
        except Exception as trace_exc:
            logger.warning("Failed to record Context assembly trace", error=str(trace_exc))
