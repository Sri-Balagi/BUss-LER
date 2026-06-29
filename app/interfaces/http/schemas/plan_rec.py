"""Plan and Recommendation API schemas — request/response DTOs."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field

from app.shared.enums import PlanStatus, RecommendationConfidence, RecommendationStatus
from app.interfaces.http.schemas.base import DomainBaseModel


# ======================= Plan Schemas =======================


class GeneratePlanRequest(DomainBaseModel):
    goal_id: Optional[UUID] = Field(
        default=None, description="Goal to generate a plan for."
    )
    intent_id: Optional[UUID] = Field(
        default=None, description="Intent that triggers the plan."
    )


class PlanStepResponse(DomainBaseModel):
    step_number: int
    action: str
    expected_outcome: str
    depends_on: List[int]
    estimated_effort: Optional[str] = None


class PlanResponse(DomainBaseModel):
    id: UUID
    twin_id: UUID
    goal_id: Optional[UUID] = None
    intent_id: Optional[UUID] = None
    rationale: str
    steps: List[PlanStepResponse]
    assumptions: List[str]
    risks: List[Dict[str, Any]]
    dependencies: List[str]
    estimated_effort: Optional[str] = None
    confidence: float
    status: PlanStatus
    cognitive_trace_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime


class PaginatedPlanResponse(DomainBaseModel):
    items: List[PlanResponse]
    total_count: int
    limit: int
    offset: int


# ======================= Recommendation Schemas =======================


class GenerateRecommendationsRequest(DomainBaseModel):
    intent_id: Optional[UUID] = Field(
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
    supporting_memory_ids: List[UUID]
    supporting_goal_ids: List[UUID]
    originating_plan_id: Optional[UUID] = None
    explainability_metadata: Dict[str, Any]
    cognitive_trace_id: Optional[UUID] = None
    acknowledged_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class PaginatedRecommendationResponse(DomainBaseModel):
    items: List[RecommendationResponse]
    total_count: int
    limit: int
    offset: int
