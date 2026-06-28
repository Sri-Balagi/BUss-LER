"""BizOS query models — inputs to service read operations.

Queries follow the CQRS pattern: one query = one intent to read state.
No mutation, no business logic. Pure data containers for read parameters.
"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import Field

from app.models.schemas import DomainBaseModel
from app.models.enums import (
    GoalStatus,
    GoalType,
    IntentStatus,
    IntentType,
    MemoryCategory,
    RecommendationStatus,
)


# =============================================================================
# Memory Queries (Milestone 2)
# =============================================================================


class MemorySearchQuery(DomainBaseModel):
    """Encapsulates parameters for searching memories."""

    twin_id: uuid.UUID
    query_text: str = Field(..., description="The semantic search string.")
    limit: int = Field(default=10, ge=1, le=100)
    threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    category: Optional[MemoryCategory] = None
    min_importance: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    include_deleted: bool = Field(default=False)


# =============================================================================
# Intent Queries (Milestone 3)
# =============================================================================


class IntentListQuery(DomainBaseModel):
    """Encapsulates parameters for listing intents."""

    twin_id: uuid.UUID
    status: Optional[IntentStatus] = Field(
        default=None, description="Filter by lifecycle status."
    )
    intent_type: Optional[IntentType] = Field(
        default=None, description="Filter by intent type."
    )
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    include_deleted: bool = Field(default=False)


# =============================================================================
# Goal Queries (Milestone 3)
# =============================================================================


class GoalListQuery(DomainBaseModel):
    """Encapsulates parameters for listing goals."""

    twin_id: uuid.UUID
    status: Optional[GoalStatus] = Field(
        default=None, description="Filter by lifecycle status."
    )
    goal_type: Optional[GoalType] = Field(
        default=None, description="Filter by goal type."
    )
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    include_deleted: bool = Field(default=False)


# =============================================================================
# Plan Queries (Milestone 3)
# =============================================================================


class PlanListQuery(DomainBaseModel):
    """Encapsulates parameters for listing plans."""

    twin_id: uuid.UUID
    goal_id: Optional[uuid.UUID] = Field(
        default=None, description="Filter by associated goal."
    )
    intent_id: Optional[uuid.UUID] = Field(
        default=None, description="Filter by originating intent."
    )
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


# =============================================================================
# Recommendation Queries (Milestone 3)
# =============================================================================


class RecommendationListQuery(DomainBaseModel):
    """Encapsulates parameters for listing recommendations."""

    twin_id: uuid.UUID
    status: Optional[RecommendationStatus] = Field(
        default=None, description="Filter by status."
    )
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


# =============================================================================
# Cognitive Trace Queries (Milestone 3)
# =============================================================================


class CognitiveTraceListQuery(DomainBaseModel):
    """Encapsulates parameters for listing cognitive traces."""

    twin_id: uuid.UUID
    operation_type: Optional[str] = Field(
        default=None,
        description=(
            "Filter by operation type. "
            "Examples: 'intent_classification', 'plan_generation', 'recommendation_generation'."
        ),
    )
    intent_id: Optional[uuid.UUID] = None
    goal_id: Optional[uuid.UUID] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
