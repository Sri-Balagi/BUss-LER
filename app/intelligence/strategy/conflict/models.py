from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class ConflictType(str, Enum):
    RESOURCE_CONTENTION = "RESOURCE_CONTENTION"
    MUTUALLY_EXCLUSIVE = "MUTUALLY_EXCLUSIVE"
    TIMELINE_OVERLAP = "TIMELINE_OVERLAP"
    POLICY_VIOLATION = "POLICY_VIOLATION"

class ConflictAssessment(BaseModel):
    """Identified conflict between objectives or goals."""
    conflict_id: str
    conflict_type: ConflictType
    description: str
    involved_objective_ids: list[str] = Field(default_factory=list)
    involved_goal_ids: list[str] = Field(default_factory=list)
