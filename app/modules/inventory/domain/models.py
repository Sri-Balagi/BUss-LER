"""Inventory Domain entities and value objects leveraging Shared Domain Kernel models."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.core.modules.kernel.kernel_models import Address, Money


class TransferStatus(str, Enum):
    PENDING = "PENDING"
    IN_TRANSIT = "IN_TRANSIT"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Warehouse(BaseModel):
    """Physical or logical storage facility."""

    warehouse_id: UUID = Field(default_factory=uuid4)
    tenant_id: str
    name: str
    code: str  # e.g. "WH-MAIN-01"
    address: Address | None = None
    is_active: bool = True


class BinLocation(BaseModel):
    """Specific shelf/bin location inside a warehouse."""

    bin_id: UUID = Field(default_factory=uuid4)
    warehouse_id: UUID
    zone: str  # e.g. "Aisle 4, Shelf B"
    code: str  # e.g. "A4-B2"


class StockItem(BaseModel):
    """Inventory Stock Item aggregate root."""

    item_id: UUID = Field(default_factory=uuid4)
    tenant_id: str
    sku: str
    name: str
    category: str
    unit_of_measure: str  # pcs, kg, boxes, liters
    quantity_on_hand: float = 0.0
    quantity_reserved: float = 0.0
    reorder_point: float = 10.0
    reorder_quantity: float = 50.0
    unit_cost: Money
    warehouse_id: UUID | None = None

    @property
    def quantity_available(self) -> float:
        return max(0.0, self.quantity_on_hand - self.quantity_reserved)

    @property
    def total_valuation(self) -> Money:
        return self.unit_cost.multiply(Decimal(str(self.quantity_on_hand)))


class StockTransfer(BaseModel):
    """Inter-warehouse or bin transfer transaction."""

    transfer_id: UUID = Field(default_factory=uuid4)
    tenant_id: str
    item_id: UUID
    source_warehouse_id: UUID
    target_warehouse_id: UUID
    quantity: float
    status: TransferStatus = TransferStatus.PENDING
    transferred_at: datetime = Field(default_factory=datetime.utcnow)


class StockAdjustment(BaseModel):
    """Audit stock adjustment (e.g. inventory audit count)."""

    adjustment_id: UUID = Field(default_factory=uuid4)
    tenant_id: str
    item_id: UUID
    quantity_delta: float  # +5 or -2
    reason: str  # AUDIT, DAMAGED, SHRINKAGE, FOUND
    adjusted_at: datetime = Field(default_factory=datetime.utcnow)


class InventoryAnalytics(BaseModel):
    """Container for Inventory Turnover & Safety Stock metrics."""

    total_sku_count: int
    total_inventory_value: Money
    inventory_turnover_ratio: float
    target_inventory_turnover: float = 6.0
    safety_stock_level: float
    economic_order_quantity: float
    shrinkage_rate_percent: float = 0.5
    recommendation: str | None = None
