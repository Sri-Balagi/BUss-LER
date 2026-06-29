"""Intent API schemas — request/response DTOs for the Intent Router.

DTOs are separate from domain models per the BizOS architecture rule.
No business logic here.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field

from app.shared.enums import IntentConfidence, IntentStatus, IntentType
from app.interfaces.http.schemas.base import DomainBaseModel


class CreateIntentRequest(DomainBaseModel):
    raw_text: str = Field(..., description="Raw natural language input from the user.")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ClassifyIntentRequest(DomainBaseModel):
    raw_text: str = Field(..., description="Raw natural language input to classify.")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IntentAnalysisResponse(DomainBaseModel):
    intent_type: IntentType
    business_domain: str
    entities: List[Dict[str, Any]]
    related_goals: List[str]
    urgency: str
    priority: int
    timeframe: Optional[str]
    confidence: IntentConfidence
    ambiguities: List[str]
    follow_up_questions: List[str]
    reasoning_metadata: Dict[str, Any]


class IntentResponse(DomainBaseModel):
    id: UUID
    twin_id: UUID
    raw_text: str
    title: Optional[str]
    intent_type: IntentType
    status: IntentStatus
    analysis: Optional[IntentAnalysisResponse] = None
    metadata: Dict[str, Any]
    classified_at: Optional[datetime] = None
    fulfilled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class ClassifyIntentResponse(DomainBaseModel):
    intent: IntentResponse
    analysis: IntentAnalysisResponse
    cognitive_trace_id: Optional[UUID] = None


class PaginatedIntentResponse(DomainBaseModel):
    items: List[IntentResponse]
    total_count: int
    limit: int
    offset: int


class UpdateIntentStatusRequest(DomainBaseModel):
    target_status: IntentStatus
