"""Goal domain models for the Intent Engine.

Pydantic v2 models representing Goals in BizOS.
Goals persist independently of conversations and are linked to intents.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field

from app.interfaces.http.schemas.base import DomainBaseModel
from app.shared.enums import GoalStatus, GoalType


class GoalBase(DomainBaseModel):
    """Base Goal schema with common attributes."""

    title: str = Field(
        ..., min_length=1, max_length=500, description="Short goal title."
    )
    description: str | None = Field(
        None, max_length=5000, description="Detailed goal description."
    )
    goal_type: GoalType = Field(
        default=GoalType.STRATEGIC,
        description="Hierarchical level of this goal.",
    )
    priority: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Priority score 1 (lowest) to 10 (highest).",
    )
    target_date: datetime | None = Field(
        None, description="Optional deadline for the goal."
    )
    success_criteria: list[str] = Field(
        default_factory=list,
        description="List of measurable success conditions.",
    )
    parent_goal_id: UUID | None = Field(
        None,
        description="Parent goal for hierarchical decomposition.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Schemaless structured metadata."
    )


class GoalCreate(GoalBase):
    """Schema for creating a new goal (write model)."""

    pass


class GoalUpdate(DomainBaseModel):
    """Schema for partially updating a goal."""

    title: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = Field(None, max_length=5000)
    goal_type: GoalType | None = None
    status: GoalStatus | None = None
    priority: int | None = Field(None, ge=1, le=10)
    progress: float | None = Field(None, ge=0.0, le=100.0)
    target_date: datetime | None = None
    success_criteria: list[str] | None = None
    metadata: dict[str, Any] | None = None


class Goal(GoalBase):
    """Full representation of a persisted Goal."""

    id: UUID
    twin_id: UUID
    status: GoalStatus = GoalStatus.DRAFT
    progress: float = Field(
        default=0.0, ge=0.0, le=100.0, description="Completion percentage 0-100."
    )
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class PaginatedGoals(DomainBaseModel):
    """Pagination wrapper for Goal listings."""

    items: list[Goal]
    total_count: int
    limit: int
    offset: int


class GoalIntentLink(DomainBaseModel):
    """Association record linking a Goal to an Intent."""

    id: UUID
    goal_id: UUID
    intent_id: UUID
    created_at: datetime
