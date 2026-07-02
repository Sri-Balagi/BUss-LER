"""Plan and Recommendation API schemas — request/response DTOs."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from app.interfaces.http.schemas.base import DomainBaseModel
from app.shared.enums import PlanStatus, RecommendationConfidence, RecommendationStatus

# ======================= Plan Schemas =======================


class GeneratePlanRequest(DomainBaseModel):
    goal_id: UUID | None = Field(default=None, description="Goal to generate a plan for.")
    intent_id: UUID | None = Field(default=None, description="Intent that triggers the plan.")


class PlanStepResponse(DomainBaseModel):
    step_number: int
    action: str
    expected_outcome: str
    depends_on: list[int]
    estimated_effort: str | None = None


class PlanResponse(DomainBaseModel):
    id: UUID
    twin_id: UUID
    goal_id: UUID | None = None
    intent_id: UUID | None = None
    rationale: str
    steps: list[PlanStepResponse]
    assumptions: list[str]
    risks: list[dict[str, Any]]
    dependencies: list[str]
    estimated_effort: str | None = None
    confidence: float
    status: PlanStatus
    cognitive_trace_id: UUID | None = None
    created_at: datetime
    updated_at: datetime


class PaginatedPlanResponse(DomainBaseModel):
    items: list[PlanResponse]
    total_count: int
    limit: int
    offset: int


# ======================= Recommendation Schemas =======================


class GenerateRecommendationsRequest(DomainBaseModel):
    intent_id: UUID | None = Field(
        default=None,
        description="Optional intent to ground recommendation generation.",
    )


class UpdateRecommendationStatusRequest(DomainBaseModel):
    target_status: RecommendationStatus


class RecommendationResponse(DomainBaseModel):
    id: UUID
    twin_id: UUID
    title: str
    body: str
    rationale: str
    confidence: RecommendationConfidence
    status: RecommendationStatus
    supporting_memory_ids: list[UUID]
    supporting_goal_ids: list[UUID]
    originating_plan_id: UUID | None = None
    explainability_metadata: dict[str, Any]
    cognitive_trace_id: UUID | None = None
    acknowledged_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class PaginatedRecommendationResponse(DomainBaseModel):
    items: list[RecommendationResponse]
    total_count: int
    limit: int
    offset: int
