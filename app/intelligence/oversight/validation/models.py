from enum import StrEnum

from pydantic import BaseModel, Field


class ValidationSeverity(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    FATAL = "FATAL"


class ValidationIssue(BaseModel):
    issue_id: str
    description: str
    severity: ValidationSeverity


class ValidationAssessment(BaseModel):
    """Result of consistency validation on an ExecutiveDecision or ExecutivePlan."""

    assessment_id: str
    is_valid: bool
    issues: list[ValidationIssue] = Field(default_factory=list)
