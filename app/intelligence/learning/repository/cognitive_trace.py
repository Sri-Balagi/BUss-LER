"""Cognitive Trace domain model.

CognitiveTrace is the standard observability layer for all BizOS cognitive operations.
It records how the AI reached a decision — purely as engineering metadata.

Design principles:
  - Completely passive: never influences business logic or AI outputs.
  - Append-only: records are never modified after creation.
  - Generic: reusable across Intent Engine (M3), Context Engine (M4),
    Agent Framework (M5), Simulation Engine (M6), and BI (M7).

Persistence responsibility: CognitiveTraceService (not the AI Kernel).
The AI Kernel exposes metadata; the service creates and persists the trace.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field

from app.interfaces.http.schemas.base import DomainBaseModel


class CognitiveTraceTokenUsage(DomainBaseModel):
    """Token consumption breakdown for an AI operation."""

    prompt_tokens: int = Field(default=0, ge=0)
    completion_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(default=0, ge=0)


class CognitiveTrace(DomainBaseModel):
    """Immutable observability record for a single cognitive AI operation.

    Created after a successful AIKernel.classify(), planning, or recommendation call.
    Used for explainability, debugging, benchmarking, and future BI analytics.

    Append-only: never modified after insert.
    """

    id: UUID
    twin_id: UUID

    # --- Operation metadata ---
    operation_type: str = Field(
        ...,
        description=(
            "The cognitive operation that produced this trace. "
            "Examples: 'intent_classification', 'plan_generation', 'recommendation_generation'."
        ),
    )
    provider: str = Field(..., description="AI provider used (e.g., 'gemini').")
    model: str = Field(
        ..., description="Exact model name used (e.g., 'gemini-2.5-flash')."
    )
    prompt_version: str = Field(
        ...,
        description=(
            "Versioned prompt ID used. "
            "Examples: 'intent_classification_v1', 'goal_planning_v1'."
        ),
    )

    # --- Request tracing ---
    operation_context_id: str = Field(
        ...,
        description="correlation_id from the OperationContext of the triggering request.",
    )

    # --- Related domain objects ---
    intent_id: UUID | None = Field(
        default=None, description="Intent that was classified or consumed."
    )
    goal_id: UUID | None = Field(
        default=None, description="Goal that was planned for or consumed."
    )
    plan_id: UUID | None = Field(
        default=None, description="Plan that was generated."
    )
    recommendation_id: UUID | None = Field(
        default=None,
        description="Recommendation that was generated.",
    )

    # --- Evidence used ---
    memory_ids_used: list[UUID] = Field(
        default_factory=list,
        description="Memory IDs retrieved and provided to the AI as context.",
    )
    goal_ids_used: list[UUID] = Field(
        default_factory=list,
        description="Goal IDs retrieved and provided to the AI as context.",
    )

    # --- AI output quality ---
    reasoning_summary: str = Field(
        ...,
        description=(
            "Engineering-facing concise explanation of how the AI reached its decision. "
            "Example: 'Intent classified as Inventory based on product stock references "
            "and recent purchasing memories.' Not exposed to end-users."
        ),
    )
    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Normalized confidence score from the AI response (0.0 to 1.0).",
    )

    # --- Performance ---
    latency_ms: float = Field(
        ..., ge=0.0, description="End-to-end AI operation latency in milliseconds."
    )
    token_usage: CognitiveTraceTokenUsage = Field(
        default_factory=CognitiveTraceTokenUsage,
        description="Token consumption breakdown.",
    )

    # --- M4 Context Observability ---
    context_id: UUID | None = Field(
        default=None, description="ID of the EnterpriseContext used."
    )
    context_sources_used: list[str] = Field(
        default_factory=list, description="List of ContextSource providers invoked."
    )
    compression_ratio: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Items retained / Items total."
    )
    ranking_latency_ms: float | None = Field(default=None, ge=0.0)
    compression_latency_ms: float | None = Field(default=None, ge=0.0)
    window_latency_ms: float | None = Field(default=None, ge=0.0)
    token_estimate: int | None = Field(
        default=None, description="Estimated context tokens consumed."
    )
    per_provider_latency_ms: dict[str, float] = Field(
        default_factory=dict,
        description="Latency per provider during Context Engine build.",
    )

    # --- Timestamps ---
    created_at: datetime

    # --- Extensibility ---
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional diagnostics or future fields.",
    )


class CognitiveTraceCreate(DomainBaseModel):
    """Write model for creating a new CognitiveTrace record."""

    twin_id: UUID
    operation_type: str
    provider: str
    model: str
    prompt_version: str
    operation_context_id: str
    intent_id: UUID | None = None
    goal_id: UUID | None = None
    plan_id: UUID | None = None
    recommendation_id: UUID | None = None
    memory_ids_used: list[UUID] = Field(default_factory=list)
    goal_ids_used: list[UUID] = Field(default_factory=list)
    reasoning_summary: str
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    latency_ms: float
    token_usage: CognitiveTraceTokenUsage = Field(
        default_factory=CognitiveTraceTokenUsage
    )

    # --- M4 Context Observability ---
    context_id: UUID | None = None
    context_sources_used: list[str] = Field(default_factory=list)
    compression_ratio: float | None = Field(default=None, ge=0.0, le=1.0)
    ranking_latency_ms: float | None = None
    compression_latency_ms: float | None = None
    window_latency_ms: float | None = None
    token_estimate: int | None = None
    per_provider_latency_ms: dict[str, float] = Field(default_factory=dict)

    metadata: dict[str, Any] = Field(default_factory=dict)


class PaginatedCognitiveTraces(DomainBaseModel):
    """Pagination wrapper for CognitiveTrace listings."""

    items: list[CognitiveTrace]
    total_count: int
    limit: int
    offset: int
