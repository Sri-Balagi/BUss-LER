"""Goal API schemas — request/response DTOs for the Goal Router."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field

from app.models.enums import GoalStatus, GoalType
from app.models.schemas import DomainBaseModel


class CreateGoalRequest(DomainBaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    goal_type: GoalType = GoalType.STRATEGIC
    priority: int = Field(default=5, ge=1, le=10)
    target_date: Optional[datetime] = None
    success_criteria: List[str] = Field(default_factory=list)
    parent_goal_id: Optional[UUID] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class UpdateGoalRequest(DomainBaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    goal_type: Optional[GoalType] = None
    priority: Optional[int] = Field(None, ge=1, le=10)
    target_date: Optional[datetime] = None
    success_criteria: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


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
    description: Optional[str] = None
    goal_type: GoalType
    status: GoalStatus
    priority: int
    progress: float
    success_criteria: List[str]
    target_date: Optional[datetime] = None
    parent_goal_id: Optional[UUID] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class PaginatedGoalResponse(DomainBaseModel):
    items: List[GoalResponse]
    total_count: int
    limit: int
    offset: int


class GoalIntentLinkResponse(DomainBaseModel):
    id: UUID
    goal_id: UUID
    intent_id: UUID
    created_at: datetime
