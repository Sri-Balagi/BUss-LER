"""Goal API schemas — request/response DTOs for the Goal Router."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field

from app.interfaces.http.schemas.base import DomainBaseModel
from app.shared.enums import GoalStatus, GoalType


class CreateGoalRequest(DomainBaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    goal_type: GoalType = GoalType.STRATEGIC
    priority: int = Field(default=5, ge=1, le=10)
    target_date: datetime | None = None
    success_criteria: list[str] = Field(default_factory=list)
    parent_goal_id: UUID | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class UpdateGoalRequest(DomainBaseModel):
    title: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    goal_type: GoalType | None = None
    priority: int | None = Field(None, ge=1, le=10)
    target_date: datetime | None = None
    success_criteria: list[str] | None = None
    metadata: dict[str, Any] | None = None


class UpdateGoalProgressRequest(DomainBaseModel):
    progress: float = Field(..., ge=0.0, le=100.0)


class UpdateGoalStatusRequest(DomainBaseModel):
    target_status: GoalStatus


class LinkIntentRequest(DomainBaseModel):
    intent_id: UUID


class GoalResponse(DomainBaseModel):
    id: UUID
    twin_id: UUID
    title: str
    description: str | None = None
    goal_type: GoalType
    status: GoalStatus
    priority: int
    progress: float
    success_criteria: list[str]
    target_date: datetime | None = None
    parent_goal_id: UUID | None = None
    completed_at: datetime | None = None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class PaginatedGoalResponse(DomainBaseModel):
    items: list[GoalResponse]
    total_count: int
    limit: int
    offset: int


class GoalIntentLinkResponse(DomainBaseModel):
    id: UUID
    goal_id: UUID
    intent_id: UUID
    created_at: datetime
