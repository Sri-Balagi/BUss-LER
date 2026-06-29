from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Any

class ConstraintType(str, Enum):
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
    constraints: List[StrategicConstraint] = Field(default_factory=list)
