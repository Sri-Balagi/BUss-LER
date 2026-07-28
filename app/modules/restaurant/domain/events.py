"""Restaurant Domain Events."""

from uuid import UUID

from app.shared.events.models import DomainEvent


class OrderPlacedEvent(DomainEvent):
    """Event emitted when a restaurant order is created."""

    order_id: UUID
    tenant_id: str | None = None
    table_number: int | None = None
    total_amount_cents: int = 0


class OrderCompletedEvent(DomainEvent):
    """Event emitted when an order is served and settled."""

    order_id: UUID
    tenant_id: str | None = None
    total_amount_cents: int = 0


class IngredientLowEvent(DomainEvent):
    """Event emitted when ingredient inventory drops below threshold."""

    ingredient_id: UUID
    ingredient_name: str
    current_stock: float
    reorder_threshold: float
    tenant_id: str | None = None


class ReservationCreatedEvent(DomainEvent):
    """Event emitted when a customer makes a table reservation."""

    reservation_id: UUID
    customer_name: str
    party_size: int
