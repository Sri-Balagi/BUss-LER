from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class GoalStatus(StrEnum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class Goal(BaseModel):
    goal_id: UUID = Field(default_factory=uuid4)
    parent_goal_id: UUID | None = None
    title: str
    description: str
    priority: int = Field(default=1)
    status: GoalStatus = Field(default=GoalStatus.PENDING)
    owner: str
    constraints: dict[str, Any] = Field(default_factory=dict)
    deadline: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    sub_goals: list[UUID] = Field(default_factory=list)

    def decompose(self, sub_goals: list['Goal']) -> None:
        """Decompose this goal into sub-goals."""
        for sg in sub_goals:
            sg.parent_goal_id = self.goal_id
            self.sub_goals.append(sg.goal_id)

    def complete(self) -> None:
        self.status = GoalStatus.COMPLETED

    def fail(self) -> None:
        self.status = GoalStatus.FAILED

    def cancel(self) -> None:
        self.status = GoalStatus.CANCELLED

    def update_priority(self, new_priority: int) -> None:
        self.priority = new_priority
