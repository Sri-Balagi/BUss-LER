from app.domain.intelligence.capability import CapabilityMetadata, CapabilityType
from app.domain.intelligence.provider import ProviderLifecycleStatus
from app.domain.planning.models import Goal, Plan, PlanningContext, PlanStep
from app.domain.planning.provider import IPlanningProvider


class DeterministicPlanningProvider(IPlanningProvider):
    """
    Mock implementation for deterministic plan generation.
    Creates predictable plans based on input goals without invoking LLMs.
    """
    
    def __init__(self, priority: int = 1, name: str = "DeterministicPlanner"):
        self._priority = priority
        self._name = name
        self._status = ProviderLifecycleStatus.READY
        
    def get_metadata(self) -> CapabilityMetadata:
        return CapabilityMetadata(
            capability_id=f"deterministic-{self._name.lower()}",
            capability_type=CapabilityType.PLANNING,
            provider_name=self._name,
            provider_version="1.0.0",
            priority=self._priority,
            supported_features=["deterministic_mocking"]
        )
        
    def set_status(self, status: ProviderLifecycleStatus) -> None:
        self._status = status
        
    def get_status(self) -> ProviderLifecycleStatus:
        return self._status
        
    async def generate_plan(self, context: PlanningContext, goal: Goal) -> Plan:
        """
        Generates a deterministic plan based on the goal description.
        """
        plan = Plan(goal_id=goal.goal_id)
        
        if "invalid" in goal.description.lower():
            # Generate a plan with a cycle to test validation
            step1 = PlanStep(action="Step 1")
            step2 = PlanStep(action="Step 2")
            plan.add_step(step1)
            plan.add_step(step2)
            plan.add_dependency(step1.step_id, step2.step_id)
            plan.add_dependency(step2.step_id, step1.step_id)  # Cycle!
        elif "orphan" in goal.description.lower():
            # Generate an orphan dependency
            import uuid
            step1 = PlanStep(action="Step 1")
            plan.add_step(step1)
            plan.add_dependency(step1.step_id, uuid.uuid4())
        else:
            # Generate a valid linear plan
            step1 = PlanStep(action="Analyze Goal", parameters={"desc": goal.description})
            step2 = PlanStep(action="Execute Action", parameters={"constraints": goal.constraints})
            plan.add_step(step1)
            plan.add_step(step2)
            plan.add_dependency(step2.step_id, step1.step_id)
            
        return plan
