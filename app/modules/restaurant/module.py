"""Restaurant Business Module implementation extending VerticalModule."""

from app.core.modules.ai.cognition import BusinessKnowledgeModel
from app.core.modules.ai.knowledge import ModuleKnowledgePack
from app.core.modules.base import VerticalModule
from app.core.modules.discovery.discovery import ModuleCapabilityDescriptor
from app.core.modules.extension_points.extension_points import ModuleExtensionPoint
from app.core.modules.models import ModuleContext
from app.core.modules.services.ui_metadata import UINavigationItem
from app.modules.restaurant.ai.cognition import RESTAURANT_KNOWLEDGE_MODEL
from app.modules.restaurant.ai.knowledge import RESTAURANT_KNOWLEDGE_PACK
from app.modules.restaurant.application.services import (
    FoodCostAnalyticsService,
    InventoryManagementService,
    KitchenDisplayService,
    OrderManagementService,
    ReservationService,
)
from app.modules.restaurant.manifest import RESTAURANT_MANIFEST


class RestaurantModule(VerticalModule):
    """Canonical Reference Restaurant Business Module for BizOS Ecosystem."""

    def __init__(self) -> None:
        super().__init__(RESTAURANT_MANIFEST)
        self.order_service = OrderManagementService()
        self.kitchen_service = KitchenDisplayService()
        self.inventory_service = InventoryManagementService()
        self.reservation_service = ReservationService()
        self.analytics_service = FoodCostAnalyticsService()

    async def initialize(self, context: ModuleContext) -> bool:
        """Initialize restaurant services, platform capabilities, extension points, and UI metadata."""
        await super().initialize(context)
        return True

    def get_knowledge_model(self) -> BusinessKnowledgeModel:
        """Expose Subsystem 1 BusinessKnowledgeModel declaration."""
        return RESTAURANT_KNOWLEDGE_MODEL

    def get_ai_knowledge_pack(self) -> ModuleKnowledgePack:
        """Expose legacy AI knowledge pack for backward compatibility."""
        return RESTAURANT_KNOWLEDGE_PACK


    def get_extension_points(self) -> list[ModuleExtensionPoint]:
        """Expose extension points for third-party modules to extend restaurant functionality."""
        return [
            ModuleExtensionPoint(
                point_id="bizos.modules.restaurant.order_processing_hook",
                module_id=self.manifest.module_id,
                name="Order Processing Interceptor Hook",
                description="Allows loyalty, tax, or discount modules to alter or enrich orders during processing."
            )
        ]

    def get_capabilities(self) -> list[ModuleCapabilityDescriptor]:
        """Expose runtime capability descriptors for AI agents."""
        return [
            ModuleCapabilityDescriptor(
                capability_id="restaurant_order_management",
                module_id=self.manifest.module_id,
                name="Restaurant Order Management",
                description="Places orders, calculates totals, and manages order lifecycle.",
                category="restaurant"
            ),
            ModuleCapabilityDescriptor(
                capability_id="restaurant_food_cost_analysis",
                module_id=self.manifest.module_id,
                name="Food Cost Analytics & Recipe Optimization",
                description="Calculates Food Cost % and optimizes recipe pricing.",
                category="analytics"
            )
        ]

    def get_ui_navigation(self) -> list[UINavigationItem]:
        """Expose declarative UI navigation menu items."""
        return [
            UINavigationItem(item_id="rest_orders", label="Dining Room Orders", icon="shopping-cart", route="/restaurant/orders", order=1),
            UINavigationItem(item_id="rest_kitchen", label="Kitchen Display (KDS)", icon="tv", route="/restaurant/kds", order=2),
            UINavigationItem(item_id="rest_analytics", label="Food Cost Analytics", icon="bar-chart-2", route="/restaurant/analytics", order=3)
        ]
