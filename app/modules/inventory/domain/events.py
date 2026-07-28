"""Inventory Domain Events."""

from uuid import UUID

from app.shared.events.models import DomainEvent


class StockReservedEvent(DomainEvent):
    """Event emitted when inventory stock is reserved for an order."""

    item_id: UUID
    quantity_reserved: float
    tenant_id: str | None = None


class StockDeductedEvent(DomainEvent):
    """Event emitted when inventory stock is physically deducted."""

    item_id: UUID
    quantity_deducted: float
    remaining_stock: float
    tenant_id: str | None = None


class ReorderPointReachedEvent(DomainEvent):
    """Event emitted when available stock drops below reorder point threshold."""

    item_id: UUID
    sku: str
    current_available: float
    reorder_point: float
    suggested_reorder_qty: float
    tenant_id: str | None = None
