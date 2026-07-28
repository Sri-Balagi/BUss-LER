"""Manifest definition for Inventory & Warehouse Horizontal Business Module."""

from app.core.modules.models import (
    MarketplaceMetadata,
    ModuleCapabilities,
    ModuleCategory,
    ModuleManifest,
    ModuleType,
)

INVENTORY_MANIFEST = ModuleManifest(
    module_id="bizos.modules.inventory.v1",
    name="Inventory & Warehouse Management",
    description="Cross-industry Enterprise Inventory & Warehouse Module for BizOS supporting Stock Control, Multi-Warehouse Locations, Transfers, Stock Deductions, Reorder Thresholds, and AI Stockout Prevention.",
    version="1.0.0",
    module_type=ModuleType.HORIZONTAL,
    category=ModuleCategory.OPERATIONS,
    author="BizOS Core Engineering Team",
    dependencies=[],
    required_connectors=["barcode_scanner", "rfid_reader", "wms_hardware"],
    supported_languages=["en", "es", "fr"],
    supported_regions=["US", "EU", "GLOBAL"],
    capabilities=ModuleCapabilities(
        domain_entities=["Warehouse", "StockItem", "BinLocation", "StockTransfer", "StockAdjustment"],
        commands=["ReserveStock", "DeductStock", "TransferStock", "AdjustStockBalance"],
        queries=["CheckStockAvailability", "GetWarehouseStock", "GetInventoryAnalytics"],
        events_published=["StockReserved", "StockDeducted", "ReorderPointReached"],
        events_subscribed=["OrderPlaced", "PurchaseOrderDelivered"],
        permissions=["inventory:stock:read", "inventory:stock:manage", "inventory:warehouse:manage"],
        ai_vocabularies=["Inventory Turnover Ratio", "Safety Stock Level", "Economic Order Quantity"],
        provided_contracts=["IInventoryProvider"]
    ),
    marketplace=MarketplaceMetadata(
        publisher="BizOS Official",
        website="https://bizos.ai/modules/inventory",
        support_email="inventory-support@bizos.ai",
        license="Enterprise-Proprietary",
        min_bizos_version="1.0.0",
        price_model="subscription",
        tags=["inventory", "warehouse", "stock", "supply_chain", "logistics", "wms"]
    ),
    configuration_schema={
        "auto_create_purchase_order_on_low_stock": {"type": "boolean", "default": True},
        "default_lead_time_days": {"type": "integer", "default": 7},
        "target_inventory_turnover": {"type": "number", "default": 6.0}
    }
)
