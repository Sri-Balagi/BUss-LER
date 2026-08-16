from enum import Enum

from pydantic import BaseModel, Field


class ObjectiveStatus(str, Enum):
    PROPOSED = "PROPOSED"
    ACTIVE = "ACTIVE"
    ON_HOLD = "ON_HOLD"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"


class ObjectivePriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class BusinessHorizon(str, Enum):
    IMMEDIATE = "IMMEDIATE"  # Days/Weeks
    SHORT_TERM = "SHORT_TERM"  # Months (Q1)
    MEDIUM_TERM = "MEDIUM_TERM"  # Quarters (H1/H2)
    LONG_TERM = "LONG_TERM"  # Years (Y1+)


class ExecutiveObjective(BaseModel):
    """A long-lived strategic outcome driven by intent."""

    objective_id: str
    description: str
    status: ObjectiveStatus = ObjectiveStatus.PROPOSED
    priority: ObjectivePriority = ObjectivePriority.MEDIUM
    horizon: BusinessHorizon = BusinessHorizon.MEDIUM_TERM
    success_criteria: list[str] = Field(default_factory=list)
    measurable_outcomes: dict[str, str] = Field(default_factory=dict)
