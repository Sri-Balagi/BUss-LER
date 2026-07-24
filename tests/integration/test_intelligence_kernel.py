import asyncio
from uuid import uuid4

import pytest

from app.bootstrap.container import Container
from app.domain.intelligence.capability import CapabilityMetadata, CapabilityType
from app.domain.intelligence.context import IntelligenceContext
from app.domain.intelligence.execution import ParallelExecution
from app.domain.intelligence.pipeline import IIntelligencePipeline, PipelineContext, PipelineResult
from app.domain.intelligence.provider import IIntelligenceProvider, ProviderLifecycleStatus
from app.domain.intelligence.telemetry import IntelligenceMetrics


class MockProvider(IIntelligenceProvider):
    def __init__(self, name: str, priority: int, status: ProviderLifecycleStatus):
        self._name = name
        self._priority = priority
        self.status = status

    def get_metadata(self) -> CapabilityMetadata:
        return CapabilityMetadata(
            capability_id=f"mock-{self._name}",
            provider_name=self._name,
            provider_version="1.0",
            capability_type=CapabilityType.REASONING,
            priority=self._priority
        )

    def get_status(self) -> ProviderLifecycleStatus:
        return self.status


class MockPipeline(IIntelligencePipeline[str, str]):
    async def execute(self, context: PipelineContext[str]) -> PipelineResult[str]:
        return PipelineResult(
            context=context.execution_context,
            payload=f"Processed: {context.payload}",
            metrics=IntelligenceMetrics(execution_time_ms=10.0)
        )


@pytest.fixture
def container():
    from app.bootstrap.container import build_container
    return build_container()


def test_registry_failover(container: Container):
    from app.domain.intelligence.provider import ICapabilityRegistry
    registry = container.resolve(ICapabilityRegistry)

    # Register priority 2 (healthy)
    p2 = MockProvider("Healthy-P2", priority=2, status=ProviderLifecycleStatus.READY)
    registry.register_provider(p2)

    # Register priority 5 (degraded/unavailable)
    p5 = MockProvider("Broken-P5", priority=5, status=ProviderLifecycleStatus.UNAVAILABLE)
    registry.register_provider(p5)

    # Resolve should skip P5 and return P2
    resolved = registry.resolve_provider(CapabilityType.REASONING)
    assert resolved is not None
    assert resolved.get_metadata().provider_name == "Healthy-P2"


@pytest.mark.asyncio
async def test_kernel_pipeline_execution(container: Container):
    from app.application.intelligence.kernel import IntelligenceKernel
    kernel = container.resolve(IntelligenceKernel)

    ctx = IntelligenceContext(tenant_id=uuid4())
    pipeline_ctx = PipelineContext(execution_context=ctx, payload="hello")
    pipeline = MockPipeline()

    result = await kernel.pipeline_manager.run_pipeline(pipeline, pipeline_ctx)
    assert result.payload == "Processed: hello"
    assert result.metrics.execution_time_ms == 10.0


@pytest.mark.asyncio
async def test_kernel_parallel_execution_policy(container: Container):
    from app.application.intelligence.kernel import IntelligenceKernel
    kernel = container.resolve(IntelligenceKernel)
    ctx = IntelligenceContext(tenant_id=uuid4())

    async def dummy_task():
        await asyncio.sleep(0.01)
        return "done"

    result = await kernel.execution_coordinator.execute_with_policy(
        ParallelExecution(),
        ctx,
        dummy_task
    )
    assert result == "done"
