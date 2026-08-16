"""Financial Accounting Domain Events."""

from uuid import UUID

from app.shared.events.models import DomainEvent


class InvoiceGeneratedEvent(DomainEvent):
    """Event emitted when an invoice is issued."""

    invoice_id: UUID
    invoice_number: str
    total_amount_cents: int = 0
    tenant_id: str | None = None


class PaymentReceivedEvent(DomainEvent):
    """Event emitted when a customer payment is settled."""

    receipt_id: UUID
    invoice_id: UUID
    amount_paid_cents: int = 0
    tenant_id: str | None = None


class FiscalPeriodClosedEvent(DomainEvent):
    """Event emitted when a fiscal accounting period is closed."""

    period_id: UUID
    period_name: str
    tenant_id: str | None = None
