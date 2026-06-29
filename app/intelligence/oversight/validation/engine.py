import uuid
from app.intelligence.decision.decision.models import ExecutiveDecision
from app.intelligence.decision.planning.models import ExecutivePlan
from app.intelligence.oversight.validation.models import ValidationAssessment, ValidationIssue, ValidationSeverity

class ExecutiveValidationEngine:
    """
    Validates consistency of decisions and plans before approval.
    """
    def validate_decision(self, decision: ExecutiveDecision) -> ValidationAssessment:
        issues = []
        if not decision.selected_alternative_id:
            issues.append(ValidationIssue(
                issue_id=str(uuid.uuid4()),
                description="Decision lacks a selected alternative.",
                severity=ValidationSeverity.FATAL
            ))
            
        return ValidationAssessment(
            assessment_id=str(uuid.uuid4()),
            is_valid=len(issues) == 0,
            issues=issues
        )
        
    def validate_plan(self, plan: ExecutivePlan) -> ValidationAssessment:
        issues = []
        if not plan.steps:
            issues.append(ValidationIssue(
                issue_id=str(uuid.uuid4()),
                description="Plan has no steps.",
                severity=ValidationSeverity.FATAL
            ))
            
        return ValidationAssessment(
            assessment_id=str(uuid.uuid4()),
            is_valid=len(issues) == 0,
            issues=issues
        )
