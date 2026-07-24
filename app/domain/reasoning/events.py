from uuid import UUID

from app.shared.events.models import DomainEvent


class ReasoningStarted(DomainEvent):
    tenant_id: UUID
    query_text: str
    target_entity_id: UUID | None = None


class ReasoningCompleted(DomainEvent):
    tenant_id: UUID
    confidence: float
    execution_time_ms: float
    provider_name: str


class ReasoningFailed(DomainEvent):
    tenant_id: UUID
    error_message: str
    provider_name: str
