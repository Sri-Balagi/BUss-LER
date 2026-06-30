"""Intent domain models for the Intent Engine.

Key types:
  IntentAnalysis  — Rich cognitive output of AIKernel.classify() (canonical object).
  Intent          — Persisted domain entity embedding IntentAnalysis.
  IntentCreate    — Write model.
  IntentUpdate    — Partial update.
  PaginatedIntents — List wrapper.

IntentAnalysis is the stable cognitive interface consumed by:
  Context Builder → Planning Engine → Recommendation Engine → M4/M5/M6/M7.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field

from app.interfaces.http.schemas.base import DomainBaseModel
from app.shared.enums import IntentConfidence, IntentStatus, IntentType

# =============================================================================
# IntentAnalysis — Canonical Cognitive Output of AIKernel.classify()
# =============================================================================


class IntentAnalysis(DomainBaseModel):
    """Rich cognitive representation of a classified intent.

    This is the canonical output of intent understanding.
    It is produced by AIKernel.classify(), validated via Pydantic before any
    service boundary is crossed, and stored as JSONB inside the Intent record.

    Future milestones (M4 Context Engine, M5 Agent Framework, M6 Simulation,
    M7 Business Intelligence) consume this object directly.

    Validation pipeline:
        AI Provider → Structured JSON → IntentAnalysis (Pydantic) →
        Business Validation → Intent (Domain) → Persistence
    """

    intent_type: IntentType = Field(
        ...,
        description="Business-domain classification (inventory, calendar, analytics, etc.).",
    )
    business_domain: str = Field(
        ...,
        max_length=255,
        description=(
            "Broader business domain context "
            "(e.g., 'Supply Chain', 'Human Resources', 'Financial Operations')."
        ),
    )
    entities: list[dict[str, Any]] = Field(
        default_factory=list,
        description=(
            "Named entities extracted from the raw text. "
            "Each entry: {'type': str, 'value': str, 'normalized': str}."
        ),
    )
    related_goals: list[str] = Field(
        default_factory=list,
        description="Goal titles or categories this intent likely contributes to.",
    )
    urgency: str = Field(
        default="normal",
        description="Urgency signal: 'low', 'normal', 'high', 'critical'.",
    )
    priority: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Inferred priority score 1 (lowest) to 10 (highest).",
    )
    timeframe: str | None = Field(
        default=None,
        description="Inferred timeframe (e.g., 'today', 'this week', 'Q4 2026', 'ASAP').",
    )
    confidence: IntentConfidence = Field(
        ...,
        description="AI classification confidence band.",
    )
    ambiguities: list[str] = Field(
        default_factory=list,
        description="Aspects of the intent that were unclear or underspecified.",
    )
    follow_up_questions: list[str] = Field(
        default_factory=list,
        description="Clarifying questions the system could ask to resolve ambiguities.",
    )
    reasoning_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "AI reasoning trace and classification diagnostics "
            "(model, prompt_version, token counts, etc.)."
        ),
    )


# =============================================================================
# Intent — Persisted Domain Entity
# =============================================================================


class IntentBase(DomainBaseModel):
    """Base Intent schema with common attributes."""

    raw_text: str = Field(
        ...,
        description="The original natural language input from the user.",
    )
    title: str | None = Field(
        None,
        max_length=255,
        description="AI-generated human-readable title (populated after classification).",
    )
    intent_type: IntentType = Field(
        default=IntentType.GENERAL,
        description="Business-domain classification (copied from IntentAnalysis after classification).",
    )
    status: IntentStatus = Field(
        default=IntentStatus.PENDING,
        description="Lifecycle status governed by IntentStateMachine.",
    )
    analysis: IntentAnalysis | None = Field(
        default=None,
        description=(
            "Full cognitive analysis produced by AIKernel.classify(). "
            "Stored as JSONB in Supabase. Null until classification completes."
        ),
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Schemaless structured metadata.",
    )


class IntentCreate(IntentBase):
    """Schema for creating a new intent (write model)."""

    pass


class IntentUpdate(DomainBaseModel):
    """Schema for partially updating an intent."""

    title: str | None = Field(None, max_length=255)
    intent_type: IntentType | None = None
    status: IntentStatus | None = None
    analysis: IntentAnalysis | None = None
    metadata: dict[str, Any] | None = None
    classified_at: datetime | None = None
    fulfilled_at: datetime | None = None


class Intent(IntentBase):
    """Full representation of a persisted Intent."""

    id: UUID
    twin_id: UUID
    classified_at: datetime | None = None
    fulfilled_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class PaginatedIntents(DomainBaseModel):
    """Pagination wrapper for Intent listings."""

    items: list[Intent]
    total_count: int
    limit: int
    offset: int
