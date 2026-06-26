"""Goal domain models for the Intent Engine.

Pydantic v2 models representing Goals in BizOS.
Goals persist independently of conversations and are linked to intents.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field

from app.models.enums import GoalStatus, GoalType
from app.models.schemas import DomainBaseModel


class GoalBase(DomainBaseModel):
    """Base Goal schema with common attributes."""

    title: str = Field(..., min_length=1, max_length=500, description="Short goal title.")
    description: Optional[str] = Field(None, max_length=5000, description="Detailed goal description.")
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
    target_date: Optional[datetime] = Field(None, description="Optional deadline for the goal.")
    success_criteria: List[str] = Field(
        default_factory=list,
        description="List of measurable success conditions.",
    )
    parent_goal_id: Optional[UUID] = Field(
        None,
        description="Parent goal for hierarchical decomposition.",
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Schemaless structured metadata.")


class GoalCreate(GoalBase):
    """Schema for creating a new goal (write model)."""

    pass


class GoalUpdate(DomainBaseModel):
    """Schema for partially updating a goal."""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    goal_type: Optional[GoalType] = None
    status: Optional[GoalStatus] = None
    priority: Optional[int] = Field(None, ge=1, le=10)
    progress: Optional[float] = Field(None, ge=0.0, le=100.0)
    target_date: Optional[datetime] = None
    success_criteria: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class Goal(GoalBase):
    """Full representation of a persisted Goal."""

    id: UUID
    twin_id: UUID
    status: GoalStatus = GoalStatus.DRAFT
    progress: float = Field(default=0.0, ge=0.0, le=100.0, description="Completion percentage 0-100.")
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class PaginatedGoals(DomainBaseModel):
    """Pagination wrapper for Goal listings."""

    items: List[Goal]
    total_count: int
    limit: int
    offset: int


class GoalIntentLink(DomainBaseModel):
    """Association record linking a Goal to an Intent."""

    id: UUID
    goal_id: UUID
    intent_id: UUID
    created_at: datetime
