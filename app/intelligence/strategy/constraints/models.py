from enum import StrEnum

from pydantic import BaseModel, Field


class ConstraintType(StrEnum):
    FINANCIAL = "FINANCIAL"
    OPERATIONAL = "OPERATIONAL"
    REGULATORY = "REGULATORY"
    CAPACITY = "CAPACITY"


class StrategicConstraint(BaseModel):
    """A dynamic business limit."""

    constraint_id: str
    constraint_type: ConstraintType
    description: str
    limit_value: float
    current_value: float
    unit: str


class StrategicConstraintSet(BaseModel):
    """Collection of currently active strategic constraints."""

    constraints: list[StrategicConstraint] = Field(default_factory=list)
