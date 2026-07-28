"""Inventory & Warehouse Business Module implementation extending HorizontalModule."""

from app.core.modules.ai.cognition import BusinessKnowledgeModel
from app.core.modules.ai.knowledge import ModuleKnowledgePack
from app.core.modules.base import HorizontalModule
from app.core.modules.discovery.discovery import ModuleCapabilityDescriptor
from app.core.modules.extension_points.extension_points import ModuleExtensionPoint
from app.core.modules.models import ModuleContext
from app.core.modules.services.ui_metadata import UINavigationItem
from app.modules.inventory.ai.cognition import INVENTORY_KNOWLEDGE_MODEL
from app.modules.inventory.ai.knowledge import INVENTORY_KNOWLEDGE_PACK
from app.modules.inventory.application.services import (
    InventoryAnalyticsService,
    InventoryService,
    WarehouseService,
)
from app.modules.inventory.manifest import INVENTORY_MANIFEST


class InventoryModule(HorizontalModule):
    """Canonical Inventory & Warehouse Business Module for BizOS Ecosystem."""

    def __init__(self) -> None:
        super().__init__(INVENTORY_MANIFEST)
        self.inventory_service = InventoryService()
        self.warehouse_service = WarehouseService()
        self.analytics_service = InventoryAnalyticsService()

    async def initialize(self, context: ModuleContext) -> bool:
        """Initialize inventory services, platform capabilities, extension points, and UI metadata."""
        await super().initialize(context)
        return True

    def get_knowledge_model(self) -> BusinessKnowledgeModel:
        """Expose Subsystem 1 BusinessKnowledgeModel declaration."""
        return INVENTORY_KNOWLEDGE_MODEL

    def get_ai_knowledge_pack(self) -> ModuleKnowledgePack:
        """Expose legacy AI knowledge pack for backward compatibility."""
        return INVENTORY_KNOWLEDGE_PACK


    def get_extension_points(self) -> list[ModuleExtensionPoint]:
        """Expose extension points for third-party modules to extend inventory functionality."""
        return [
            ModuleExtensionPoint(
                point_id="bizos.modules.inventory.reorder_calculation_hook",
                module_id=self.manifest.module_id,
                name="Reorder Point Calculation Interceptor Hook",
                description="Allows predictive AI or supplier integrations to dynamically alter reorder thresholds."
            )
        ]

    def get_capabilities(self) -> list[ModuleCapabilityDescriptor]:
        """Expose runtime capability descriptors for AI agents."""
        return [
            ModuleCapabilityDescriptor(
                capability_id="inventory_stock_control",
                module_id=self.manifest.module_id,
                name="Inventory Stock Control & Reservation",
                description="Checks availability, reserves stock, and deducts inventory.",
                category="operations"
            ),
            ModuleCapabilityDescriptor(
                capability_id="inventory_turnover_analytics",
                module_id=self.manifest.module_id,
                name="Inventory Turnover & EOQ Analytics",
                description="Calculates turnover ratios, Economic Order Quantity, and safety stock levels.",
                category="analytics"
            )
        ]

    def get_ui_navigation(self) -> list[UINavigationItem]:
        """Expose declarative UI navigation menu items."""
        return [
            UINavigationItem(item_id="inv_stock", label="Stock Control & SKUs", icon="package", route="/inventory/stock", order=1),
            UINavigationItem(item_id="inv_warehouses", label="Warehouse Locations", icon="home", route="/inventory/warehouses", order=2),
            UINavigationItem(item_id="inv_analytics", label="Stock Analytics & EOQ", icon="pie-chart", route="/inventory/analytics", order=3)
        ]
