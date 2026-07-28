"""CRM Domain Events."""

from uuid import UUID

from app.shared.events.models import DomainEvent


class LeadCreatedEvent(DomainEvent):
    """Event emitted when a new sales lead is created."""

    lead_id: UUID
    first_name: str
    last_name: str
    tenant_id: str | None = None


class OpportunityWonEvent(DomainEvent):
    """Event emitted when a deal is closed won."""

    opportunity_id: UUID
    customer_id: UUID
    deal_value_cents: int = 0
    tenant_id: str | None = None


class OpportunityLostEvent(DomainEvent):
    """Event emitted when a deal is closed lost."""

    opportunity_id: UUID
    customer_id: UUID
    reason: str | None = None
    tenant_id: str | None = None


class PipelineStageUpdatedEvent(DomainEvent):
    """Event emitted when a deal advances in the sales pipeline."""

    opportunity_id: UUID
    previous_stage: str
    new_stage: str
    tenant_id: str | None = None
