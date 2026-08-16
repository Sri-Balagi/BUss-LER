"""Unit tests for Inventory & Warehouse Horizontal Business Module."""

from decimal import Decimal
from uuid import uuid4

import pytest

from app.core.modules.kernel.kernel_models import Money
from app.core.modules.manager import ModuleManager
from app.core.modules.models import ModuleContext
from app.core.modules.registry import ModuleRegistry
from app.modules.inventory.domain.models import BinLocation, StockItem, Warehouse
from app.modules.inventory.module import InventoryModule


@pytest.mark.asyncio
async def test_inventory_module_full_lifecycle():
    module = InventoryModule()
    registry = ModuleRegistry()
    manager = ModuleManager(registry=registry)
    ctx = ModuleContext(tenant_id="inv_tenant_01")

    # Install & Initialize
    assert await manager.install_module(module, ctx) is True
    assert await manager.initialize_module(module.manifest.module_id, ctx) is True
    assert await manager.enable_module(module.manifest.module_id, ctx) is True

    # Test Warehouse Creation
    wh_id = uuid4()
    warehouse = Warehouse(
        warehouse_id=wh_id,
        tenant_id="inv_tenant_01",
        name="Central Logistics Hub",
        code="WH-CENTRAL-01"
    )
    await module.warehouse_service.create_warehouse(warehouse)

    bin_loc = BinLocation(
        warehouse_id=wh_id,
        zone="Aisle 1",
        code="A1-B04"
    )
    await module.warehouse_service.create_bin(bin_loc)

    # Test IInventoryProvider Contract Implementation
    item_id = uuid4()
    stock_item = StockItem(
        item_id=item_id,
        tenant_id="inv_tenant_01",
        sku="SKU-MICROCHIP-101",
        name="Silicon Microchip Core i9",
        category="Electronics",
        unit_of_measure="pcs",
        quantity_on_hand=100.0,
        reorder_point=20.0,
        reorder_quantity=50.0,
        unit_cost=Money(amount=Decimal("45.00")),
        warehouse_id=wh_id
    )
    await module.inventory_service.add_stock_item(stock_item)

    # Check availability
    is_avail = await module.inventory_service.check_availability("inv_tenant_01", str(item_id), 30.0)
    assert is_avail is True

    # Reserve stock
    reserved = await module.inventory_service.reserve_stock("inv_tenant_01", str(item_id), 30.0, "REF-ORD-101")
    assert reserved is True

    # Deduct stock
    deducted = await module.inventory_service.deduct_stock("inv_tenant_01", str(item_id), 85.0, "REF-ORD-101")
    assert deducted is True
    # 100 - 85 = 15 on hand (<= 20 reorder point)

    # Test Inventory Analytics
    cogs_annual = Money(amount=Decimal("120000.00"))
    analytics = module.analytics_service.calculate_inventory_analytics([stock_item], cogs_annual, target_turnover=6.0)
    assert analytics.total_sku_count == 1
    assert analytics.economic_order_quantity > 0.0

    # Verify Declarative Business Knowledge Model (Subsystem 1)
    km = module.get_knowledge_model()
    assert km is not None
    assert len(km.vocabulary.terms) >= 2
    assert len(km.decision_frameworks) >= 1

    # Verify AI Knowledge Pack (Backward Compatibility)
    ai_pack = module.get_ai_knowledge_pack()
    assert len(ai_pack.vocabularies) >= 2


    # Verify Extension Points & Capabilities
    assert len(module.get_extension_points()) >= 1
    assert len(module.get_capabilities()) >= 2
    assert len(module.get_ui_navigation()) >= 3
