from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class GoalState(str, Enum):
    CREATED = "CREATED"
    PENDING = "PENDING"
    REASONING = "REASONING"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    IN_PROGRESS = "IN_PROGRESS"
    WAITING = "WAITING"
    REPLANNING = "REPLANNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


GoalStatus = GoalState


class Goal(BaseModel):
    goal_id: UUID = Field(default_factory=uuid4)
    parent_goal_id: UUID | None = None
    title: str
    description: str
    priority: int = Field(default=1)
    status: GoalStatus = Field(default=GoalStatus.PENDING)
    state: GoalState = Field(default=GoalState.CREATED)
    history: list[str] = Field(default_factory=list)
    owner: str
    constraints: dict[str, Any] = Field(default_factory=dict)
    deadline: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sub_goals: list[UUID] = Field(default_factory=list)

    def set_state(self, new_state: GoalState) -> None:
        self.state = new_state
        self.status = new_state
        self.history.append(f"{new_state.value}:{datetime.now(timezone.utc).isoformat()}")

    def decompose(self, sub_goals: list['Goal']) -> None:
        """Decompose this goal into sub-goals."""
        for sg in sub_goals:
            sg.parent_goal_id = self.goal_id
            self.sub_goals.append(sg.goal_id)

    def complete(self) -> None:
        self.set_state(GoalState.COMPLETED)

    def fail(self) -> None:
        self.set_state(GoalState.FAILED)

    def cancel(self) -> None:
        self.set_state(GoalState.CANCELLED)

    def update_priority(self, new_priority: int) -> None:
        self.priority = new_priority
