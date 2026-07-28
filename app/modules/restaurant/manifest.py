"""Manifest definition for Restaurant Business Module."""

from app.core.modules.models import (
    MarketplaceMetadata,
    ModuleCapabilities,
    ModuleCategory,
    ModuleManifest,
    ModuleType,
)

RESTAURANT_MANIFEST = ModuleManifest(
    module_id="bizos.modules.restaurant.v1",
    name="Restaurant & Food Service Management",
    description="Canonical Enterprise Restaurant Module for BizOS supporting Orders, Menus, Recipes, Kitchen Display, Inventory, Reservations, and AI Food Cost optimization.",
    version="1.0.0",
    module_type=ModuleType.VERTICAL,
    category=ModuleCategory.RESTAURANT,
    author="BizOS Core Engineering Team",
    dependencies=[],
    required_connectors=["pos_terminal", "kitchen_display", "payment_gateway"],
    supported_languages=["en", "es", "fr"],
    supported_regions=["US", "EU", "GLOBAL"],
    capabilities=ModuleCapabilities(
        domain_entities=["Order", "MenuItem", "Recipe", "Ingredient", "Table", "Reservation", "KitchenTicket", "Supplier"],
        commands=["CreateOrder", "UpdateKitchenTicket", "ReserveTable", "UpdateRecipeCost"],
        queries=["GetActiveOrders", "GetKitchenQueue", "GetFoodCostAnalytics"],
        events_published=["OrderPlaced", "OrderCompleted", "IngredientLow", "ReservationCreated"],
        events_subscribed=["PaymentReceived", "SupplierShipmentDelivered"],
        permissions=["restaurant:order:create", "restaurant:kitchen:manage", "restaurant:reports:view"],
        ai_vocabularies=["Food Cost Percentage", "Table Turnaround Rate", "Kitchen Bottleneck Index"],
        provided_contracts=["IRestaurantOrderProvider"]
    ),
    marketplace=MarketplaceMetadata(
        publisher="BizOS Official",
        website="https://bizos.ai/modules/restaurant",
        support_email="restaurant-support@bizos.ai",
        license="Enterprise-Proprietary",
        min_bizos_version="1.0.0",
        price_model="subscription",
        tags=["restaurant", "food_service", "kitchen", "hospitality", "pos"]
    ),
    configuration_schema={
        "tax_rate_percent": {"type": "number", "default": 8.5},
        "auto_print_kitchen_tickets": {"type": "boolean", "default": True},
        "target_food_cost_percent": {"type": "number", "default": 30.0}
    }
)
