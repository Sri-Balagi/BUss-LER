"""Intent API schemas — request/response DTOs for the Intent Router.

DTOs are separate from domain models per the BizOS architecture rule.
No business logic here.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from app.interfaces.http.schemas.base import DomainBaseModel
from app.shared.enums import IntentConfidence, IntentStatus, IntentType


class CreateIntentRequest(DomainBaseModel):
    raw_text: str = Field(..., description="Raw natural language input from the user.")
    metadata: dict[str, Any] = Field(default_factory=dict)


class ClassifyIntentRequest(DomainBaseModel):
    raw_text: str = Field(..., description="Raw natural language input to classify.")
    metadata: dict[str, Any] = Field(default_factory=dict)


class IntentAnalysisResponse(DomainBaseModel):
    intent_type: IntentType
    business_domain: str
    entities: list[dict[str, Any]]
    related_goals: list[str]
    urgency: str
    priority: int
    timeframe: str | None
    confidence: IntentConfidence
    ambiguities: list[str]
    follow_up_questions: list[str]
    reasoning_metadata: dict[str, Any]


class IntentResponse(DomainBaseModel):
    id: UUID
    twin_id: UUID
    raw_text: str
    title: str | None
    intent_type: IntentType
    status: IntentStatus
    analysis: IntentAnalysisResponse | None = None
    metadata: dict[str, Any]
    classified_at: datetime | None = None
    fulfilled_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class ClassifyIntentResponse(DomainBaseModel):
    intent: IntentResponse
    analysis: IntentAnalysisResponse
    cognitive_trace_id: UUID | None = None


class PaginatedIntentResponse(DomainBaseModel):
    items: list[IntentResponse]
    total_count: int
    limit: int
    offset: int


class UpdateIntentStatusRequest(DomainBaseModel):
    target_status: IntentStatus
