import uuid

import pytest

from app.bootstrap.container import build_container, reset_container_for_testing
from app.domain.cognition.events import LearningRequested
from app.domain.intelligence.capability import CapabilityType
from app.domain.intelligence.events import (
    CapabilityExecutionCompleted,
    CapabilityExecutionStarted,
    UnifiedExecutionCompleted,
    UnifiedExecutionStarted,
)
from app.domain.intelligence.platform import IIntelligencePlatform, UnifiedExecutionRequest
from app.domain.intelligence.provider import ICapabilityRegistry
from app.infrastructure.learning.mock_provider import MockLearningProvider
from app.infrastructure.workflow.mock_provider import MockWorkflowIntelligenceProvider
from app.shared.events.bus import AsyncioEventBus, EventBus


class MockEventBus(EventBus):
    def __init__(self):
        self.published_events = []
    def subscribe(self, event_type, handler):
        pass
    def unsubscribe(self, event_type, handler):
        pass
    def publish(self, event):
        self.published_events.append(event)

@pytest.fixture
def container():
    reset_container_for_testing()
    c = build_container()

    mock_bus = MockEventBus()
    c.override(EventBus, mock_bus)

    # We need to register mock providers for our capabilities to avoid exceptions
    registry = c.resolve(ICapabilityRegistry)
    registry.register_provider(MockLearningProvider())
    registry.register_provider(MockWorkflowIntelligenceProvider())

    class MockRetrievalProvider:
        capability_type = CapabilityType.RETRIEVAL
        priority = 100

        def get_metadata(self):
            class Meta:
                capability_id = "mock_retrieval"
                capability_type = CapabilityType.RETRIEVAL
                priority = 100
                tags = []
            return Meta()

        def get_status(self):
            return "READY"

    class MockAgentProvider:

        def get_metadata(self):
            class Meta:
                capability_id = "mock_agent"
                capability_type = CapabilityType.AGENT
                priority = 100
                tags = []
            return Meta()

        def get_status(self):
            return "READY"

    registry.register_provider(MockRetrievalProvider())
    registry.register_provider(MockAgentProvider())

    yield c
    reset_container_for_testing()


@pytest.mark.asyncio
async def test_platform_resolution(container):
    platform = container.resolve(IIntelligencePlatform)
    assert platform is not None
    assert type(platform).__name__ == "UnifiedIntelligencePlatform"


@pytest.mark.asyncio
async def test_execute_request_orchestration(container):
    platform = container.resolve(IIntelligencePlatform)
    container.resolve(EventBus)

    req = UnifiedExecutionRequest(
        request_type="retrieval",
        tenant_id=uuid.uuid4(),
        input_data={"query": "test"},
        correlation_id=str(uuid.uuid4())
    )

    result = await platform.execute_request(req)

    assert result.success is True
    assert "retrieval" in result.metrics.capabilities_invoked


@pytest.mark.asyncio
async def test_agent_execution_dispatch(container):
    platform = container.resolve(IIntelligencePlatform)
    container.resolve(EventBus)

    agent_id = uuid.uuid4()
    result = await platform.execute_agent_goal(agent_id, "test goal")

    assert result.success is True


@pytest.mark.asyncio
async def test_workflow_optimization(container):
    platform = container.resolve(IIntelligencePlatform)

    wf_id = uuid.uuid4()
    result = await platform.optimize_workflow(wf_id)

    assert result.success is True
    assert "workflow" in result.metrics.capabilities_invoked


@pytest.mark.asyncio
async def test_provider_failover(container):
    platform = container.resolve(IIntelligencePlatform)
    registry = container.resolve(ICapabilityRegistry)

    # Create a degraded provider and a healthy lower-priority one
    class DegradedProvider:

        def get_metadata(self):
            class Meta:
                capability_id = "degraded_reasoning"
                capability_type = CapabilityType.REASONING
                priority = 100
                tags = []
            return Meta()

        def get_status(self):
            return "DEGRADED"

    class ReadyProvider:

        def get_metadata(self):
            class Meta:
                capability_id = "ready_reasoning"
                capability_type = CapabilityType.REASONING
                priority = 50
                tags = []
            return Meta()

        def get_status(self):
            return "READY"

    registry.register_provider(DegradedProvider())
    registry.register_provider(ReadyProvider())

    # The registry should resolve ReadyProvider
    provider = registry.resolve_provider(CapabilityType.REASONING)
    assert provider is not None
    assert provider.get_metadata().capability_id == "ready_reasoning"

    req = UnifiedExecutionRequest(
        request_type="reasoning",
        tenant_id=uuid.uuid4(),
        input_data={"logic": "test"},
        correlation_id=str(uuid.uuid4())
    )
    result = await platform.execute_request(req)
    assert result.success is True


@pytest.mark.asyncio
async def test_telemetry_aggregation(container):
    platform = container.resolve(IIntelligencePlatform)

    req = UnifiedExecutionRequest(
        request_type="agent",
        tenant_id=uuid.uuid4(),
        input_data={"goal": "telemetry test"},
        correlation_id=str(uuid.uuid4())
    )
    result = await platform.execute_request(req)

    assert result.metrics is not None
    assert result.correlation_id == req.correlation_id
    assert "agent" in result.metrics.capabilities_invoked

    status = await platform.get_execution_status(req.correlation_id)
    assert status["status"] == "COMPLETED"
