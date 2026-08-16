from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.application.intelligence.kernel import IntelligenceKernel
from app.application.reasoning.service import ReasoningEngineService
from app.application.twin.service import DigitalTwinService
from app.bootstrap.container import Container, build_container, reset_container_for_testing
from app.domain.intelligence.capability import CapabilityType
from app.domain.intelligence.provider import ICapabilityRegistry, ProviderLifecycleStatus
from app.domain.reasoning.models import ReasoningContext, ReasoningQuery
from app.infrastructure.reasoning.mock_provider import MockReasoningProvider


@pytest.fixture
def container():
    reset_container_for_testing()
    cont = build_container()
    yield cont
    reset_container_for_testing()


@pytest.mark.asyncio
async def test_reasoning_capability_failover(container: Container):
    """Test registry resolves priority 100 first, then priority 50 after degraded."""
    registry = container.resolve(ICapabilityRegistry)

    # Use very high priorities (100/50) to dominate any pre-registered providers
    provider_b = MockReasoningProvider(priority=50, name="ProviderB")
    provider_a = MockReasoningProvider(priority=100, name="ProviderA")

    registry.register_provider(provider_b)
    registry.register_provider(provider_a)

    # 1. Resolve should yield ProviderA (priority 100)
    resolved = registry.resolve_provider(CapabilityType.REASONING)
    assert resolved.get_metadata().provider_name == "ProviderA"

    # 2. Transition ProviderA to DEGRADED
    provider_a.set_status(ProviderLifecycleStatus.DEGRADED)

    # 3. Resolve should yield ProviderB (priority 50, READY)
    resolved_again = registry.resolve_provider(CapabilityType.REASONING)
    assert resolved_again.get_metadata().provider_name == "ProviderB"


@pytest.mark.asyncio
async def test_reasoning_pipeline_execution(container: Container):
    """Test the full reasoning pipeline including digital twin grounding and events."""
    from app.application.reasoning.pipeline import ReasoningPipeline
    twin_service = container.resolve(DigitalTwinService)
    registry = container.resolve(ICapabilityRegistry)

    # Register a top-priority mock (priority=9999) so it ALWAYS dominates any real providers
    top_mock = MockReasoningProvider(priority=9999, name="TopMockProvider")
    registry.register_provider(top_mock)

    # Build a fresh pipeline using the updated registry to guarantee mock is used
    from app.application.intelligence.kernel import IntelligenceKernel
    kernel = container.resolve(IntelligenceKernel)
    pipeline = ReasoningPipeline(
        capability_registry=registry,
        twin_service=twin_service,
        event_router=kernel.event_router
    )

    # Wrap in a dedicated service using the fresh pipeline
    from app.application.reasoning.service import ReasoningEngineService
    service = ReasoningEngineService(kernel=kernel, pipeline=pipeline)

    tenant_id = uuid4()
    entity_id = uuid4()

    context = ReasoningContext(tenant_id=tenant_id)

    # 1. Create a Twin so we can ground
    await twin_service.create_twin(context, entity_id, "Employee")
    await twin_service.update_twin_properties(context, entity_id, {"role": "Engineer"})

    query = ReasoningQuery(
        query_text="Summarize the employee role.",
        required_schema={"type": "object"}
    )

    # 2. Execute Reasoning Pipeline
    response = await service.execute_reasoning(context, query, entity_id=entity_id)

    assert response is not None
    # The mock provider returns confidence=0.99 (confirms top-priority mock was used)
    assert response.confidence == 0.99
    # Payload is either the raw dict or coerced by Pydantic — verify it's truthy / correct type
    assert response.payload is not None

    # 3. Verify Grounding (active_twin should be in context_data for provider, returned in metadata mock)
    active_twin = response.provider_metadata.get("active_twin")
    assert active_twin is not None
    assert str(active_twin["entity_id"]) == str(entity_id)
    assert active_twin["properties"]["role"] == "Engineer"

