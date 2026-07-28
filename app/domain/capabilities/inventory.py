"""Reusable Horizontal Inventory Capability Module."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class SKUItem(BaseModel):
    sku: str
    name: str
    stock_quantity: int
    reorder_threshold: int = 15
    unit_cost_usd: float = 25.0


class InventoryCapabilityModule:
    """Horizontal Inventory capability engine."""

    def __init__(self):
        self._items: Dict[str, SKUItem] = {}

    def register_item(self, item: SKUItem) -> None:
        self._items[item.sku] = item

    def deduct_stock(self, sku: str, quantity: int) -> Dict[str, Any]:
        if sku not in self._items:
            raise KeyError(f"SKU '{sku}' not found in inventory.")
        item = self._items[sku]
        item.stock_quantity = max(0, item.stock_quantity - quantity)
        needs_reorder = item.stock_quantity <= item.reorder_threshold
        return {
            "sku": sku,
            "remaining_stock": item.stock_quantity,
            "needs_reorder": needs_reorder,
            "alert": f"LOW STOCK WARNING for {item.name}" if needs_reorder else "OK",
        }
