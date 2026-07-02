from enum import Enum

from pydantic import BaseModel, Field


class DecisionPriority(str, Enum):
    ROUTINE = "ROUTINE"
    IMPORTANT = "IMPORTANT"
    URGENT = "URGENT"
    CRITICAL = "CRITICAL"


class DecisionAlternative(BaseModel):
    """A candidate option considered by the Decision Engine."""

    alternative_id: str
    description: str
    estimated_value: float
    constraint_compliance: bool = True
    policy_compliance: bool = True


class ExecutiveDecision(BaseModel):
    """The formal, reasoned decision produced by the Decision Engine."""

    decision_id: str
    objective_id: str
    selected_alternative_id: str
    rationale: str
    priority: DecisionPriority = DecisionPriority.ROUTINE
    alternatives_considered: list[DecisionAlternative] = Field(default_factory=list)
