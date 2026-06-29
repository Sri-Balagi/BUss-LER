import uuid
from typing import List, Optional
from app.intelligence.intake.intent.models import ExecutiveIntent
from app.intelligence.strategy.objectives.models import (
    ExecutiveObjective, ObjectiveStatus, ObjectivePriority, BusinessHorizon
)

class ExecutiveObjectivesEngine:
    """
    Creates and maintains the lifecycle of long-term executive objectives.
    """
    def create_objective_from_intent(self, intent: ExecutiveIntent) -> ExecutiveObjective:
        # Determine priority and horizon based on classification (mock logic)
        priority = ObjectivePriority.MEDIUM
        horizon = BusinessHorizon.MEDIUM_TERM
        
        if intent.classification.value == "STRATEGIC_OBJECTIVE":
            priority = ObjectivePriority.HIGH
            horizon = BusinessHorizon.LONG_TERM
        elif intent.classification.value == "ESCALATION":
            priority = ObjectivePriority.CRITICAL
            horizon = BusinessHorizon.IMMEDIATE
            
        description = f"Objective derived from: {intent.raw_request}"
        
        return ExecutiveObjective(
            objective_id=str(uuid.uuid4()),
            description=description,
            status=ObjectiveStatus.PROPOSED,
            priority=priority,
            horizon=horizon,
            success_criteria=intent.requested_outcomes,
            measurable_outcomes={}
        )

    def activate_objective(self, objective: ExecutiveObjective) -> ExecutiveObjective:
        objective.status = ObjectiveStatus.ACTIVE
        return objective
