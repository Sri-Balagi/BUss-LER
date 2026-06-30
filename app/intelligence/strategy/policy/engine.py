from app.intelligence.strategy.objectives.models import ExecutiveObjective
from app.intelligence.strategy.policy.models import PolicyAssessment, PolicyStatus, PolicyViolation


class BusinessPolicyEngine:
    """
    Evaluates business rules against strategic decisions.
    """

    def evaluate_objective(self, objective: ExecutiveObjective) -> PolicyAssessment:
        violations = []

        # Mock policy: No critical priorities unless horizon is immediate
        if objective.priority.value == "CRITICAL" and objective.horizon.value != "IMMEDIATE":
            violations.append(PolicyViolation(
                policy_id="POL_001",
                description="CRITICAL priority objectives must have an IMMEDIATE business horizon.",
                severity="HIGH"
            ))

        if violations:
            return PolicyAssessment(status=PolicyStatus.VIOLATION, violations=violations)

        return PolicyAssessment(status=PolicyStatus.COMPLIANT, violations=[])
