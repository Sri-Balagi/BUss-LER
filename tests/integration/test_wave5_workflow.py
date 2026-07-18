import pytest
import asyncio
from uuid import uuid4

from app.bootstrap.container import build_container, reset_container_for_testing, Container
from app.domain.intelligence.capability import CapabilityType
from app.domain.intelligence.provider import ICapabilityRegistry
from app.application.workflow.service import WorkflowIntelligenceService
from app.domain.workflow.models import (
    WorkflowOptimizationContext,
    WorkflowState
)
from app.intelligence.executive.workflow import Workflow, WorkflowTask
from app.application.intelligence.kernel import IntelligenceKernel
from app.domain.workflow.events import (
    WorkflowOptimizationStarted,
    WorkflowOptimizationCompleted,
    WorkflowOptimized
)

@pytest.fixture
def container():
    reset_container_for_testing()
    c = build_container()
    
    c.resolve("workflow_registry_initializer")
    
    yield c
    reset_container_for_testing()


@pytest.fixture
def test_workflow():
    wf = Workflow()
    wf.add_task(WorkflowTask(capability_id="test_cap_1", payload={"foo": "bar"}))
    wf.add_task(WorkflowTask(capability_id="test_cap_2", payload={"baz": "qux"}))
    return wf


@pytest.mark.asyncio
async def test_workflow_capability_resolution(container: Container):
    """Test that the workflow optimization capability is registered in the registry."""
    registry = container.resolve(ICapabilityRegistry)
    
    providers = registry.resolve_all_providers(CapabilityType.WORKFLOW)
    assert len(providers) >= 1
    
    provider = registry.resolve_provider(CapabilityType.WORKFLOW)
    assert provider is not None
    assert provider.get_metadata().provider_name == "MockWorkflowOptimizer"


from app.shared.events.bus import EventBus

@pytest.mark.asyncio
async def test_workflow_optimization_pipeline(container: Container, test_workflow: Workflow):
    """Test that the WorkflowIntelligenceService can optimize a workflow."""
    service = container.resolve(WorkflowIntelligenceService)
    event_router = container.resolve(IntelligenceKernel).event_router
    
    # Setup mock event handler to capture events
    captured_events = []
    
    original_publish = event_router.publish
    
    async def mock_publish(event):
        captured_events.append(event)
        await original_publish(event)
        
    event_router.publish = mock_publish
    
    context = WorkflowOptimizationContext(
        execution_id=uuid4(),
        workflow=test_workflow
    )
    
    result = await service.optimize_workflow(context)
    
    # Wait for async event bus handlers

    
    # Verify state changes
    assert result.state == WorkflowState.COMPLETED
    assert "Mock optimization complete" in result.optimization_suggestions
    assert result.workflow is not None
    assert len(result.workflow.tasks) == 2
    
    # Verify events
    event_types = [e.event_type for e in captured_events]
    assert "workflow.optimization.started" in event_types
    assert "workflow.optimization.optimized" in event_types
    assert "workflow.optimization.completed" in event_types
    
    # Assert telemetry is embedded
    completed_event = next(e for e in captured_events if e.event_type == "workflow.optimization.completed")
    assert completed_event.optimization_time_ms >= 0.0
