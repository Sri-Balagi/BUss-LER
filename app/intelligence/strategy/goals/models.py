from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional

class GoalStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Goal(BaseModel):
    """A tactical goal derived from a strategic objective."""
    goal_id: str
    objective_id: str
    description: str
    status: GoalStatus = GoalStatus.PENDING
    parent_goal_id: Optional[str] = None
    subgoal_ids: List[str] = Field(default_factory=list)

class GoalCollection(BaseModel):
    """A managed hierarchy of active and pending goals."""
    objective_id: str
    goals: List[Goal] = Field(default_factory=list)
