"""Recommendation domain models for the Recommendation Engine.

Recommendations are first-class cognitive artifacts.
They are proactive, explainable suggestions generated from the twin's
goals, memories, plans, and business context.

Validation pipeline:
    AI Provider → Structured JSON → Recommendation (Pydantic) →
    Business Validation → Recommendation (Domain) → Persistence
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from app.interfaces.http.schemas.base import DomainBaseModel
from app.shared.enums import RecommendationConfidence, RecommendationStatus


class RecommendationBase(DomainBaseModel):
    """Base Recommendation schema with common attributes."""

    title: str = Field(
        ...,
        max_length=255,
        description="Short title summarising the recommendation.",
    )
    body: str = Field(
        ...,
        description="Full recommendation text presented to the user.",
    )
    rationale: str = Field(
        ...,
        description="AI-generated reasoning explaining why this is recommended.",
    )
    confidence: RecommendationConfidence = Field(
        default=RecommendationConfidence.MEDIUM,
        description="AI confidence in the recommendation.",
    )
    supporting_memory_ids: list[UUID] = Field(
        default_factory=list,
        description="IDs of Memory records that informed this recommendation.",
    )
    supporting_goal_ids: list[UUID] = Field(
        default_factory=list,
        description="IDs of Goal records that this recommendation addresses or advances.",
    )
    originating_plan_id: UUID | None = Field(
        default=None,
        description="Plan that generated or triggered this recommendation, if any.",
    )
    trigger_context: dict[str, Any] = Field(
        default_factory=dict,
        description="Snapshot of context data that triggered this recommendation.",
    )
    explainability_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Engineering-facing explainability data "
            "(model, prompt_version, reasoning summary, evidence references). "
            "Not exposed to end-users."
        ),
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Schemaless structured metadata.",
    )


class RecommendationCreate(RecommendationBase):
    """Schema for creating a new recommendation (write model)."""

    pass


class Recommendation(RecommendationBase):
    """Full representation of a persisted Recommendation.

    Recommendations are immutable after creation.
    User responses (accepted/rejected) update only the status field.
    """

    id: UUID
    twin_id: UUID
    status: RecommendationStatus = RecommendationStatus.NEW
    created_at: datetime
    updated_at: datetime
    acknowledged_at: datetime | None = None


class PaginatedRecommendations(DomainBaseModel):
    """Pagination wrapper for Recommendation listings."""

    items: list[Recommendation]
    total_count: int
    limit: int
    offset: int
