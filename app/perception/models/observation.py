import enum
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

from app.perception.models.extracted_entities import ExtractedEntities


class ObservationSourceType(str, enum.Enum):
    CONNECTOR = "CONNECTOR"
    CRM = "CRM"
    AGENT = "AGENT"
    SENSOR = "SENSOR"
    VOICE = "VOICE"
    VISION = "VISION"
    USER_ACTION = "USER_ACTION"
    INTERNAL_SYSTEM = "INTERNAL_SYSTEM"


class ExternalObservation(BaseModel):
    """Raw signal emitted by any IObservationSource."""

    observation_id: str = Field(default_factory=lambda: str(uuid4()))
    source_id: str = Field(..., description="Identifier of the source e.g. google_drive, slack")
    source_type: ObservationSourceType = Field(default=ObservationSourceType.CONNECTOR)
    observed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resource_id: str = Field(default="", description="Provider record ID")
    resource_type: str = Field(..., description="Type of resource e.g. file, email, event, commit")
    title: str = Field(default="", description="Human-readable title of the resource")
    raw_content: str = Field(default="", description="Serialized raw payload string")
    content_type: str = Field(default="application/json")
    raw_payload: dict[str, Any] = Field(default_factory=dict, description="Raw provider JSON payload")
    tenant_id: str | None = None


class BusinessEventType(str, enum.Enum):
    # Generic Entity & State Transitions (Universal Wave -1)
    ENTITY_CREATED = "ENTITY_CREATED"
    ENTITY_UPDATED = "ENTITY_UPDATED"
    STATE_TRANSITION = "STATE_TRANSITION"
    AGREEMENT_EXECUTED = "AGREEMENT_EXECUTED"
    MILESTONE_REACHED = "MILESTONE_REACHED"

    # Agreements & Decisions
    PROPOSAL_CREATED = "PROPOSAL_CREATED"
    APPROVAL_RECEIVED = "APPROVAL_RECEIVED"
    CONTRACT_SIGNED = "CONTRACT_SIGNED"
    DECISION_RECORDED = "DECISION_RECORDED"

    # Project Lifecycle
    MILESTONE_SCHEDULED = "MILESTONE_SCHEDULED"
    DEADLINE_SET = "DEADLINE_SET"
    TASK_ASSIGNED = "TASK_ASSIGNED"
    DELIVERABLE_UPLOADED = "DELIVERABLE_UPLOADED"

    # Relationships & CRM Lifecycle
    NEW_LEAD = "NEW_LEAD"
    LEAD_QUALIFIED = "LEAD_QUALIFIED"
    OPPORTUNITY_CREATED = "OPPORTUNITY_CREATED"
    DEAL_STAGE_CHANGED = "DEAL_STAGE_CHANGED"
    DEAL_WON = "DEAL_WON"
    DEAL_LOST = "DEAL_LOST"
    FOLLOW_UP_SCHEDULED = "FOLLOW_UP_SCHEDULED"
    MEETING_LOGGED = "MEETING_LOGGED"
    QUOTE_SENT = "QUOTE_SENT"
    INVOICE_PAID = "INVOICE_PAID"
    SUPPORT_TICKET_CREATED = "SUPPORT_TICKET_CREATED"
    CLIENT_COMMUNICATION = "CLIENT_COMMUNICATION"
    TEAM_MEETING_SCHEDULED = "TEAM_MEETING_SCHEDULED"

    # Technical & Operations
    BUG_REPORTED = "BUG_REPORTED"
    FEATURE_IMPLEMENTED = "FEATURE_IMPLEMENTED"
    ARCHITECTURE_DOCUMENTED = "ARCHITECTURE_DOCUMENTED"


class BusinessEvent(BaseModel):
    """Detected business event within an observation."""

    event_type: BusinessEventType
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    evidence: str | None = None
    detected_entities: list[str] = Field(default_factory=list)


class IntelligenceGateDecision(str, enum.Enum):
    ACCEPT = "ACCEPT"
    SUMMARIZE = "SUMMARIZE"
    DISCARD = "DISCARD"


class UnifiedKnowledgeObject(BaseModel):
    """Observation normalized into a provider-agnostic form."""

    uko_id: str = Field(..., description="Unique deterministic identifier e.g. SHA256 of source+resource_id")
    source_connector: str = Field(default="")
    source_id: str = Field(default="", description="Connector/source that emitted this UKO")
    source_observation_id: str = Field(default="")
    resource_type: str
    entity_type: str | None = Field(default=None, description="Canonical entity type e.g. Contact, Deal, Company")
    title: str
    content: str = Field(default="", description="Extracted plain text content")
    author: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_url: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    extracted_entities: ExtractedEntities | None = None
    embedding: list[float] | None = None
    knowledge_node_id: UUID | None = None
    gate_decision: IntelligenceGateDecision = IntelligenceGateDecision.ACCEPT
    detected_events: list[BusinessEvent] = Field(default_factory=list)
