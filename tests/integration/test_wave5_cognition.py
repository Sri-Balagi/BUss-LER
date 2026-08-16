import asyncio
from uuid import uuid4

import pytest

from app.application.cognition.service import CognitiveEngineService
from app.application.intelligence.kernel import IntelligenceKernel
from app.bootstrap.container import Container, build_container
from app.domain.cognition.events import (
    CognitiveCycleCompleted,
    CognitiveCycleStarted,
    LearningRequested,
    ReflectionGenerated,
)
from app.domain.cognition.models import AgentState, AgentStatus, ReflectionFeedback
from app.domain.intelligence.capability import CapabilityType
from app.domain.intelligence.provider import ICapabilityRegistry


@pytest.fixture
def container():
    c = build_container()

    # Run the registry initializer to add the MockAgentImplementation
    c.resolve("cognition_registry_initializer")

    return c


@pytest.mark.asyncio
async def test_cognition_capability_resolution(container: Container):
    """Test that the agent capability is correctly registered in the ICapabilityRegistry."""
    registry = container.resolve(ICapabilityRegistry)

    # Fetch agents
    providers = registry.resolve_all_providers(CapabilityType.AGENT)
    assert len(providers) >= 1

    # Check default mock agent is returned
    agent_provider = registry.resolve_provider(CapabilityType.AGENT)
    assert agent_provider is not None
    assert agent_provider.get_metadata().provider_name == "DefaultAgent"


@pytest.mark.asyncio
async def test_cognitive_pipeline_execution_success(container: Container):
    """Test that the cognitive pipeline executes successfully with correct events."""
    service = container.resolve(CognitiveEngineService)
    kernel = container.resolve(IntelligenceKernel)

    published_events = []

    async def capture_event(event):
        published_events.append(event)

    kernel.event_router._event_bus.subscribe(CognitiveCycleStarted, capture_event)
    kernel.event_router._event_bus.subscribe(CognitiveCycleCompleted, capture_event)
    kernel.event_router._event_bus.subscribe(ReflectionGenerated, capture_event)
    kernel.event_router._event_bus.subscribe(LearningRequested, capture_event)

    tenant_id = uuid4()
    agent_id = uuid4()
    context = AgentState(
        tenant_id=tenant_id,
        agent_id=agent_id,
        status=AgentStatus.IDLE
    )

    # Execute the loop
    result_state = await service.execute_agent_loop(context)

    # Assert state
    assert result_state.status == AgentStatus.COMPLETED
    assert result_state.reflection_feedback == ReflectionFeedback.IS_COMPLETE
    assert result_state.current_iteration == 1
    assert len(result_state.execution_history) == 1

    # Allow async bus to process
    await asyncio.sleep(0.1)

    # Assert events
    assert any(isinstance(e, CognitiveCycleStarted) for e in published_events)
    assert any(isinstance(e, ReflectionGenerated) for e in published_events)
    assert any(isinstance(e, LearningRequested) for e in published_events)
    assert any(isinstance(e, CognitiveCycleCompleted) for e in published_events)


@pytest.mark.asyncio
async def test_cognitive_pipeline_max_iterations(container: Container):
    """Test that the cognitive pipeline aborts gracefully if it hits max_iterations without completing."""
    service = container.resolve(CognitiveEngineService)

    tenant_id = uuid4()
    agent_id = uuid4()
    context = AgentState(
        tenant_id=tenant_id,
        agent_id=agent_id,
        status=AgentStatus.IDLE,
        reflection_feedback=ReflectionFeedback.NEEDS_REPLAN  # Force it to loop forever
    )

    # Execute the loop
    result_state = await service.execute_agent_loop(context)

    # Assert state
    # max_iterations default is 5
    assert result_state.status == AgentStatus.FAILED
    assert result_state.reflection_feedback == ReflectionFeedback.FAILED
    assert result_state.current_iteration == 5
