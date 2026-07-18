import time
from typing import Dict, Any
from app.domain.intelligence.pipeline import IIntelligencePipeline, PipelineContext, PipelineResult
from app.domain.intelligence.telemetry import IntelligenceMetrics
from app.domain.intelligence.provider import ICapabilityRegistry
from app.domain.intelligence.capability import CapabilityType
from app.application.twin.service import DigitalTwinService
from app.domain.reasoning.models import ReasoningContext, ReasoningQuery, ReasoningResponse
from app.domain.reasoning.events import ReasoningStarted, ReasoningCompleted, ReasoningFailed
from app.application.intelligence.kernel import EventRouter

class ReasoningPipeline(IIntelligencePipeline[Dict[str, Any], ReasoningResponse]):
    
    def __init__(
        self, 
        capability_registry: ICapabilityRegistry,
        twin_service: DigitalTwinService,
        event_router: EventRouter
    ):
        self._registry = capability_registry
        self._twin_service = twin_service
        self._event_router = event_router
        
    async def execute(self, context: PipelineContext[Dict[str, Any]]) -> PipelineResult[ReasoningResponse]:
        start_time = time.perf_counter()
        
        reasoning_context: ReasoningContext = context.execution_context # type: ignore
        query: ReasoningQuery = context.payload["query"]
        entity_id = context.payload.get("entity_id")
        
        # 1. Resolve Active Digital Twin State
        if entity_id:
            twin = await self._twin_service.get_twin(reasoning_context, entity_id)
            if twin:
                # Add to context_data for grounding
                query.context_data["active_twin"] = twin.model_dump()
                
        # 2. Publish ReasoningStarted
        await self._event_router.publish(ReasoningStarted(
            correlation_id=reasoning_context.correlation_id,
            tenant_id=reasoning_context.tenant_id, # type: ignore
            query_text=query.query_text,
            target_entity_id=entity_id
        ))
        
        # 3. Resolve Provider
        provider = self._registry.resolve_provider(CapabilityType.REASONING)
        if not provider:
            error_msg = "No READY/DEGRADED Reasoning Provider found in Capability Registry."
            await self._event_router.publish(ReasoningFailed(
                correlation_id=reasoning_context.correlation_id,
                tenant_id=reasoning_context.tenant_id, # type: ignore
                error_message=error_msg,
                provider_name="Unknown"
            ))
            raise RuntimeError(error_msg)
            
        provider_name = provider.get_metadata().provider_name
            
        # 4. Execute Reasoning
        try:
            # We don't construct prompts here. We pass context and query directly.
            response: ReasoningResponse = await provider.reason(reasoning_context, query) # type: ignore
            
            execution_time = (time.perf_counter() - start_time) * 1000
            
            # 5. Publish ReasoningCompleted
            await self._event_router.publish(ReasoningCompleted(
                correlation_id=reasoning_context.correlation_id,
                tenant_id=reasoning_context.tenant_id, # type: ignore
                confidence=response.confidence,
                execution_time_ms=execution_time,
                provider_name=provider_name
            ))
            
            # 6. Return Pipeline Result
            return PipelineResult(
                context=reasoning_context,
                payload=response,
                metrics=IntelligenceMetrics(execution_time_ms=execution_time)
            )
            
        except Exception as e:
            await self._event_router.publish(ReasoningFailed(
                correlation_id=reasoning_context.correlation_id,
                tenant_id=reasoning_context.tenant_id, # type: ignore
                error_message=str(e),
                provider_name=provider_name
            ))
            raise e
