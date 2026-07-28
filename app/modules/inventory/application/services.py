"""Inventory Application Services implementing stock control & warehouse workflows."""

import logging
import math
from decimal import Decimal
from uuid import UUID

from app.core.modules.contracts.contracts import IInventoryProvider
from app.core.modules.kernel.kernel_models import Money
from app.modules.inventory.domain.events import (
    ReorderPointReachedEvent,
    StockDeductedEvent,
    StockReservedEvent,
)
from app.modules.inventory.domain.models import (
    BinLocation,
    InventoryAnalytics,
    StockItem,
    Warehouse,
)
from app.shared.events.bus import EventBus

logger = logging.getLogger(__name__)


class InventoryService(IInventoryProvider):
    """Inventory service implementing the IInventoryProvider module contract."""

    def __init__(self, event_bus: EventBus | None = None) -> None:
        self._items: dict[str, StockItem] = {}
        self._event_bus = event_bus

    async def add_stock_item(self, item: StockItem) -> StockItem:
        """Register or update a stock item."""
        self._items[str(item.item_id)] = item
        logger.info(f"Registered stock item {item.item_id} SKU={item.sku}")
        return item

    async def get_stock_item(self, item_id: str) -> StockItem | None:
        """Retrieve stock item by ID."""
        return self._items.get(item_id)

    async def check_availability(self, tenant_id: str, item_id: str, required_qty: float) -> bool:
        """Check if stock item has sufficient available stock."""
        item = self._items.get(item_id)
        if not item or item.tenant_id != tenant_id:
            return False
        return item.quantity_available >= required_qty

    async def reserve_stock(self, tenant_id: str, item_id: str, qty: float, reference_id: str) -> bool:
        """Reserve inventory quantity for an order."""
        item = self._items.get(item_id)
        if not item or item.tenant_id != tenant_id or item.quantity_available < qty:
            return False

        item.quantity_reserved += qty
        logger.info(f"Reserved {qty} of item {item_id} for ref {reference_id}")

        if self._event_bus:
            self._event_bus.publish(
                StockReservedEvent(
                    correlation_id=reference_id,
                    item_id=UUID(item_id),
                    quantity_reserved=qty,
                    tenant_id=tenant_id
                )
            )

        return True

    async def deduct_stock(self, tenant_id: str, item_id: str, qty: float, reference_id: str) -> bool:
        """Permanently deduct stock and check reorder threshold."""
        item = self._items.get(item_id)
        if not item or item.tenant_id != tenant_id or item.quantity_on_hand < qty:
            return False

        item.quantity_on_hand -= qty
        if item.quantity_reserved >= qty:
            item.quantity_reserved -= qty

        logger.info(f"Deducted {qty} of item {item_id} remaining={item.quantity_on_hand}")

        if self._event_bus:
            self._event_bus.publish(
                StockDeductedEvent(
                    correlation_id=reference_id,
                    item_id=UUID(item_id),
                    quantity_deducted=qty,
                    remaining_stock=item.quantity_on_hand,
                    tenant_id=tenant_id
                )
            )

            if item.quantity_available <= item.reorder_point:
                self._event_bus.publish(
                    ReorderPointReachedEvent(
                        correlation_id=reference_id,
                        item_id=UUID(item_id),
                        sku=item.sku,
                        current_available=item.quantity_available,
                        reorder_point=item.reorder_point,
                        suggested_reorder_qty=item.reorder_quantity,
                        tenant_id=tenant_id
                    )
                )

        return True


class WarehouseService:
    """Service managing warehouse facilities and bin locations."""

    def __init__(self) -> None:
        self._warehouses: dict[UUID, Warehouse] = {}
        self._bins: dict[UUID, BinLocation] = {}

    async def create_warehouse(self, warehouse: Warehouse) -> Warehouse:
        """Create a new warehouse facility."""
        self._warehouses[warehouse.warehouse_id] = warehouse
        return warehouse

    async def create_bin(self, bin_loc: BinLocation) -> BinLocation:
        """Create a shelf/bin location in a warehouse."""
        self._bins[bin_loc.bin_id] = bin_loc
        return bin_loc


class InventoryAnalyticsService:
    """Service computing Inventory Turnover Ratio, EOQ, and Safety Stock."""

    @staticmethod
    def calculate_inventory_analytics(
        items: list[StockItem],
        cogs_annual: Money,
        annual_demand_units: float = 1000.0,
        order_cost: float = 50.0,
        holding_cost_per_unit: float = 5.0,
        target_turnover: float = 6.0
    ) -> InventoryAnalytics:
        """Calculate inventory valuation, turnover, and Economic Order Quantity (EOQ)."""
        total_val = Money(amount=Decimal("0.00"))
        for item in items:
            total_val = total_val.add(item.total_valuation)

        avg_inventory_val = total_val.amount
        if avg_inventory_val == Decimal("0.00"):
            turnover = 0.0
        else:
            turnover = float(cogs_annual.amount / avg_inventory_val)

        # EOQ = sqrt((2 * Demand * OrderCost) / HoldingCost)
        eoq = math.sqrt((2.0 * annual_demand_units * order_cost) / holding_cost_per_unit) if holding_cost_per_unit > 0 else 0.0
        safety_stock = 1.65 * math.sqrt(7.0) * 10.0  # 95% service level approx

        rec = None
        if turnover < target_turnover and len(items) > 0:
            rec = f"Inventory turnover ratio ({turnover:.1f}x) is below target ({target_turnover:.1f}x). Recommend liquidating slow-moving SKUs to free up working capital."

        return InventoryAnalytics(
            total_sku_count=len(items),
            total_inventory_value=total_val,
            inventory_turnover_ratio=round(turnover, 2),
            target_inventory_turnover=target_turnover,
            safety_stock_level=round(safety_stock, 1),
            economic_order_quantity=round(eoq, 1),
            recommendation=rec
        )
