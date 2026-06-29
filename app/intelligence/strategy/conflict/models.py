from enum import Enum
from pydantic import BaseModel, Field
from typing import List

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
    involved_objective_ids: List[str] = Field(default_factory=list)
    involved_goal_ids: List[str] = Field(default_factory=list)
