from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class GoalStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class Goal(BaseModel):
    goal_id: UUID = Field(default_factory=uuid4)
    parent_goal_id: Optional[UUID] = None
    title: str
    description: str
    priority: int = Field(default=1)
    status: GoalStatus = Field(default=GoalStatus.PENDING)
    owner: str
    constraints: Dict[str, Any] = Field(default_factory=dict)
    deadline: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sub_goals: List[UUID] = Field(default_factory=list)

    def decompose(self, sub_goals: List['Goal']) -> None:
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
