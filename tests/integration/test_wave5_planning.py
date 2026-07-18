import pytest
import asyncio
from uuid import uuid4

from app.bootstrap.container import build_container, reset_container_for_testing, Container
from app.domain.intelligence.capability import CapabilityType
from app.domain.intelligence.provider import ICapabilityRegistry, ProviderLifecycleStatus
from app.domain.planning.models import Goal, PlanningContext, PlanStatus
from app.domain.planning.events import PlanGenerationStarted, PlanValidationFailed, PlanValidationSucceeded, PlanGenerated
from app.application.planning.service import PlanningEngineService
from app.infrastructure.planning.deterministic_provider import DeterministicPlanningProvider
from app.application.intelligence.kernel import IntelligenceKernel
from app.domain.twin.models import TwinSnapshot
from app.domain.reasoning.models import ReasoningResponse


@pytest.fixture
def container():
    reset_container_for_testing()
    cont = build_container()
    yield cont
    reset_container_for_testing()


@pytest.mark.asyncio
async def test_planning_capability_resolution(container: Container):
    """Test registry successfully routes to the Planning provider."""
    registry = container.resolve(ICapabilityRegistry)
    
    # Provider is registered in DI automatically
    resolved = registry.resolve_provider(CapabilityType.PLANNING)
    assert resolved is not None
    assert resolved.get_metadata().provider_name == "DefaultDeterministicPlanner"
    
    # Degrade it, another one should be picked if available (only one here, so it's degraded, resolve returns None unless another exists)
    resolved.set_status(ProviderLifecycleStatus.DEGRADED)
    
    # Add another READY one
    provider_b = DeterministicPlanningProvider(priority=5, name="FallbackPlanner")
    registry.register_provider(provider_b)
    
    resolved_again = registry.resolve_provider(CapabilityType.PLANNING)
    assert resolved_again.get_metadata().provider_name == "FallbackPlanner"


@pytest.mark.asyncio
async def test_planning_pipeline_valid_execution(container: Container):
    """Test pipeline generates and validates a correct plan successfully."""
    service = container.resolve(PlanningEngineService)
    kernel = container.resolve(IntelligenceKernel)
    
    # Setup test event listening
    published_events = []
    
    async def capture_event(event):
        published_events.append(event)
        
    # Subscribe to relevant events
    kernel.event_router._event_bus.subscribe(PlanGenerationStarted, capture_event)
    kernel.event_router._event_bus.subscribe(PlanValidationSucceeded, capture_event)
    kernel.event_router._event_bus.subscribe(PlanGenerated, capture_event)

    tenant_id = uuid4()
    context = PlanningContext(
        tenant_id=tenant_id,
        active_twin=TwinSnapshot(entity_id=uuid4(), entity_type="System", state={}),
        reasoning_result=ReasoningResponse(confidence=0.9, payload={}, provider_metadata={})
    )
    
    goal = Goal(description="Create a valid linear plan.")
    
    plan = await service.create_plan(context, goal)
    
    assert plan is not None
    assert plan.status == PlanStatus.VALIDATED
    assert len(plan.steps) == 2
    assert len(plan.dependencies) == 1
    
    # Allow event bus to process
    await asyncio.sleep(0.1)
    
    # Check events
    assert any(isinstance(e, PlanGenerationStarted) for e in published_events)
    assert any(isinstance(e, PlanValidationSucceeded) for e in published_events)
    assert any(isinstance(e, PlanGenerated) for e in published_events)


@pytest.mark.asyncio
async def test_planning_pipeline_cycle_validation(container: Container):
    """Test pipeline detects cycles and fails validation."""
    service = container.resolve(PlanningEngineService)
    kernel = container.resolve(IntelligenceKernel)
    
    published_events = []
    async def capture_event(event):
        published_events.append(event)
        
    kernel.event_router._event_bus.subscribe(PlanValidationFailed, capture_event)

    context = PlanningContext(tenant_id=uuid4())
    goal = Goal(description="invalid cycle")
    
    plan = await service.create_plan(context, goal)
    
    assert plan is not None
    assert plan.status == PlanStatus.INVALID
    assert len(plan.validation_errors) > 0
    assert "Cyclic dependency detected" in plan.validation_errors[0]
    
    # Allow event bus to process
    await asyncio.sleep(0.1)
    
    # Event should be published
    assert any(isinstance(e, PlanValidationFailed) for e in published_events)


@pytest.mark.asyncio
async def test_planning_pipeline_orphan_validation(container: Container):
    """Test pipeline detects missing prerequisite steps."""
    service = container.resolve(PlanningEngineService)

    context = PlanningContext(tenant_id=uuid4())
    goal = Goal(description="orphan dependency")
    
    plan = await service.create_plan(context, goal)
    
    assert plan is not None
    assert plan.status == PlanStatus.INVALID
    assert len(plan.validation_errors) > 0
    assert "Dependency references non-existent depends_on_step_id" in plan.validation_errors[0]
