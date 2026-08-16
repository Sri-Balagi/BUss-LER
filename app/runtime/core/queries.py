"""BizOS query models — inputs to service read operations.

Queries follow the CQRS pattern: one query = one intent to read state.
No mutation, no business logic. Pure data containers for read parameters.
"""

import uuid
from datetime import datetime

from pydantic import Field

from app.interfaces.http.schemas.base import DomainBaseModel
from app.shared.enums import (
    GoalStatus,
    GoalType,
    IntentStatus,
    IntentType,
    RecommendationStatus,
)

# =============================================================================
# Memory Queries
# =============================================================================


class MemorySearchQuery(DomainBaseModel):
    """Encapsulates parameters for searching memories."""

    twin_id: uuid.UUID
    query_text: str = Field(..., description="The semantic search string.")
    limit: int = Field(default=10, ge=1, le=100)
    threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    category: str | None = None
    min_importance: float | None = Field(default=None, ge=0.0, le=1.0)
    start_date: datetime | None = None
    end_date: datetime | None = None
    include_deleted: bool = Field(default=False)


# =============================================================================
# Intent Queries
# =============================================================================


class IntentListQuery(DomainBaseModel):
    """Encapsulates parameters for listing intents."""

    twin_id: uuid.UUID
    status: IntentStatus | None = Field(default=None, description="Filter by lifecycle status.")
    intent_type: IntentType | None = Field(default=None, description="Filter by intent type.")
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    include_deleted: bool = Field(default=False)


# =============================================================================
# Goal Queries
# =============================================================================


class GoalListQuery(DomainBaseModel):
    """Encapsulates parameters for listing goals."""

    twin_id: uuid.UUID
    status: GoalStatus | None = Field(default=None, description="Filter by lifecycle status.")
    goal_type: GoalType | None = Field(default=None, description="Filter by goal type.")
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    include_deleted: bool = Field(default=False)


# =============================================================================
# Plan Queries
# =============================================================================


class PlanListQuery(DomainBaseModel):
    """Encapsulates parameters for listing plans."""

    twin_id: uuid.UUID
    goal_id: uuid.UUID | None = Field(default=None, description="Filter by associated goal.")
    intent_id: uuid.UUID | None = Field(default=None, description="Filter by originating intent.")
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


# =============================================================================
# Recommendation Queries
# =============================================================================


class RecommendationListQuery(DomainBaseModel):
    """Encapsulates parameters for listing recommendations."""

    twin_id: uuid.UUID
    status: RecommendationStatus | None = Field(default=None, description="Filter by status.")
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


# =============================================================================
# Cognitive Trace Queries
# =============================================================================


class CognitiveTraceListQuery(DomainBaseModel):
    """Encapsulates parameters for listing cognitive traces."""

    twin_id: uuid.UUID
    operation_type: str | None = Field(
        default=None,
        description=(
            "Filter by operation type. "
            "Examples: 'intent_classification', 'plan_generation', 'recommendation_generation'."
        ),
    )
    intent_id: uuid.UUID | None = None
    goal_id: uuid.UUID | None = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
