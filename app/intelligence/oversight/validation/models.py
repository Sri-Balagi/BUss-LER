from enum import Enum
from pydantic import BaseModel, Field
from typing import List

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
    issues: List[ValidationIssue] = Field(default_factory=list)
