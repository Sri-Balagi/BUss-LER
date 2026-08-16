import uuid

from app.intelligence.decision.decision.models import ExecutiveDecision
from app.intelligence.decision.planning.models import (
    ExecutiveDirective,
    ExecutivePlan,
    PlanningDependency,
    PlanningStep,
)


class PlanningEngine:
    """
    Translates an Executive Decision into a structured, dependency-ordered Executive Plan
    and generates the final Directives to be handed off to the Supervisor.
    Never creates Runtime Tasks.
    """

    def generate_plan(self, decision: ExecutiveDecision) -> ExecutivePlan:
        step1 = PlanningStep(
            step_id="step1",
            action_description=f"Initial phase for {decision.rationale}",
            estimated_effort_hours=40.0,
        )
        step2 = PlanningStep(
            step_id="step2", action_description="Execution phase", estimated_effort_hours=80.0
        )

        directive = ExecutiveDirective(
            directive_id=str(uuid.uuid4()),
            intent=f"Execute decision {decision.decision_id}",
            success_conditions=["Plan executed fully"],
        )

        return ExecutivePlan(
            plan_id=str(uuid.uuid4()),
            decision_id=decision.decision_id,
            steps=[step1, step2],
            dependencies=[PlanningDependency(step_id="step2", depends_on_step_id="step1")],
            generated_directives=[directive],
        )
