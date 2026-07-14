from enum import StrEnum

from pydantic import BaseModel, Field


class GoalStatus(StrEnum):
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
    parent_goal_id: str | None = None
    subgoal_ids: list[str] = Field(default_factory=list)


class GoalCollection(BaseModel):
    """A managed hierarchy of active and pending goals."""

    objective_id: str
    goals: list[Goal] = Field(default_factory=list)
