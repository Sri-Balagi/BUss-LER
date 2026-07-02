"""Plan domain models for the Planning Engine.

Plans are first-class cognitive artifacts.
They represent AI-generated future execution strategies and become
inputs for Agent Framework (M5), Simulation Engine (M6), and BI (M7).

Validation pipeline:
    AI Provider → Structured JSON → Plan/PlanStep (Pydantic) →
    Business Validation → Plan (Domain) → Persistence
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from app.interfaces.http.schemas.base import DomainBaseModel
from app.shared.enums import PlanStatus


class PlanStep(DomainBaseModel):
    """A single step within an execution plan."""

    step_number: int = Field(..., ge=1, description="Ordered position of this step.")
    action: str = Field(..., description="Human-readable description of the action to take.")
    expected_outcome: str = Field(..., description="What should happen if this step succeeds.")
    depends_on: list[int] = Field(
        default_factory=list,
        description="Step numbers this step depends on completing first.",
    )
    estimated_effort: str | None = Field(
        default=None,
        description="Effort estimate for this step (e.g., '30 minutes', '2 hours', '1 day').",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional additional step-level context.",
    )


class PlanBase(DomainBaseModel):
    """Base Plan schema with common attributes."""

    rationale: str = Field(
        ...,
        description="AI-generated reasoning explaining why this plan addresses the goal.",
    )
    steps: list[PlanStep] = Field(
        ...,
        min_length=1,
        description="Ordered list of steps to achieve the goal.",
    )
    assumptions: list[str] = Field(
        default_factory=list,
        description="Assumptions made by the planner that must hold for this plan to be valid.",
    )
    risks: list[dict[str, Any]] = Field(
        default_factory=list,
        description=(
            "Identified risks and mitigations. "
            "Each entry: {'risk': str, 'likelihood': str, 'mitigation': str}."
        ),
    )
    dependencies: list[str] = Field(
        default_factory=list,
        description="External resources, systems, or actors required by this plan.",
    )
    estimated_effort: str | None = Field(
        default=None,
        description="Total effort estimate (e.g., '1 week', '3 days').",
    )
    confidence: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="AI confidence score in this plan (0.0 to 1.0).",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Schemaless structured metadata.",
    )


class PlanCreate(PlanBase):
    """Schema for creating a new plan (write model)."""

    pass


class Plan(PlanBase):
    """Full representation of a persisted Plan.

    Plans are never modified post-generation.
    Revisions are new Plan records linked to the same goal/intent.
    """

    id: UUID
    twin_id: UUID
    goal_id: UUID | None = Field(
        default=None,
        description="The goal this plan addresses (if goal-directed).",
    )
    intent_id: UUID | None = Field(
        default=None,
        description="The intent that triggered this plan (if intent-directed).",
    )
    status: PlanStatus = PlanStatus.DRAFT
    created_at: datetime
    updated_at: datetime


class PaginatedPlans(DomainBaseModel):
    """Pagination wrapper for Plan listings."""

    items: list[Plan]
    total_count: int
    limit: int
    offset: int
