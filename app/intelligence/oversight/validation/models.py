from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class ValidationSeverity(str, Enum):
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
