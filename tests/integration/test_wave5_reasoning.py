from datetime import UTC, datetime
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
    """Test registry resolves priority 10 first, then priority 5 after degraded."""
    registry = container.resolve(ICapabilityRegistry)

    provider_b = MockReasoningProvider(priority=5, name="ProviderB")
    provider_a = MockReasoningProvider(priority=10, name="ProviderA")

    registry.register_provider(provider_b)
    registry.register_provider(provider_a)

    # 1. Resolve should yield ProviderA (priority 10)
    resolved = registry.resolve_provider(CapabilityType.REASONING)
    assert resolved.get_metadata().provider_name == "ProviderA"

    # 2. Transition ProviderA to DEGRADED
    provider_a.set_status(ProviderLifecycleStatus.DEGRADED)

    # 3. Resolve should yield ProviderB (priority 5, READY)
    resolved_again = registry.resolve_provider(CapabilityType.REASONING)
    assert resolved_again.get_metadata().provider_name == "ProviderB"


@pytest.mark.asyncio
async def test_reasoning_pipeline_execution(container: Container):
    """Test the full reasoning pipeline including digital twin grounding and events."""
    service = container.resolve(ReasoningEngineService)
    twin_service = container.resolve(DigitalTwinService)

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
    assert response.confidence == 0.99
    assert response.payload == {"status": "success", "mocked_from_schema": True}

    # 3. Verify Grounding (active_twin should be in context_data for provider, returned in metadata mock)
    active_twin = response.provider_metadata.get("active_twin")
    assert active_twin is not None
    assert str(active_twin["entity_id"]) == str(entity_id)
    assert active_twin["properties"]["role"] == "Engineer"
