from enum import Enum

from pydantic import BaseModel, Field


class PolicyStatus(str, Enum):
    COMPLIANT = "COMPLIANT"
    VIOLATION = "VIOLATION"


class PolicyViolation(BaseModel):
    policy_id: str
    description: str
    severity: str


class PolicyAssessment(BaseModel):
    """Evaluation against static business rules."""

    status: PolicyStatus
    violations: list[PolicyViolation] = Field(default_factory=list)
