"""Unit tests for Canonical Reference Restaurant Business Module."""

from decimal import Decimal
from uuid import uuid4

import pytest

from app.core.modules.kernel.kernel_models import Money
from app.core.modules.manager import ModuleManager
from app.core.modules.models import ModuleContext
from app.core.modules.registry import ModuleRegistry
from app.modules.restaurant.domain.models import Ingredient, OrderItem, Recipe
from app.modules.restaurant.module import RestaurantModule


@pytest.mark.asyncio
async def test_restaurant_module_full_lifecycle():
    module = RestaurantModule()
    registry = ModuleRegistry()
    manager = ModuleManager(registry=registry)
    ctx = ModuleContext(tenant_id="rest_tenant_01")

    # Install & Initialize
    assert await manager.install_module(module, ctx) is True
    assert await manager.initialize_module(module.manifest.module_id, ctx) is True
    assert await manager.enable_module(module.manifest.module_id, ctx) is True

    # Test Order placement
    item1 = OrderItem(
        item_id=uuid4(),
        item_name="Burger Special",
        quantity=2,
        unit_price=Money(amount=Decimal("12.50"))
    )

    order = await module.order_service.create_order(
        tenant_id="rest_tenant_01",
        table_number=5,
        items=[item1]
    )

    assert order.total_amount.amount == Decimal("25.00")

    # Complete Order
    completed = await module.order_service.complete_order(order.order_id)
    assert completed.status.value == "COMPLETED"

    # Test Kitchen Display System
    ticket = await module.kitchen_service.create_ticket(order)
    assert ticket.status == "QUEUED"
    updated_ticket = await module.kitchen_service.update_ticket_status(ticket.ticket_id, "COOKING")
    assert updated_ticket.status == "COOKING"

    # Test Recipe Food Cost Calculation
    recipe = Recipe(
        name="Cheeseburger Recipe",
        ingredients=[{"ingredient_id": "ing_beef", "qty": 0.25}]
    )
    ingredient_costs = {"ing_beef": Money(amount=Decimal("8.00"))}  # $8 per lb
    raw_cost = recipe.calculate_raw_cost(ingredient_costs)
    assert raw_cost.amount == Decimal("2.00")

    # Test Food Cost Analytics
    revenue = Money(amount=Decimal("1000.00"))
    cogs = Money(amount=Decimal("350.00"))  # 35% food cost
    analytics = module.analytics_service.calculate_food_cost(revenue, cogs, target_cost_pct=30.0)

    assert analytics.food_cost_percentage == 35.0
    assert "Food cost (35.0%) exceeds target" in analytics.recommendation

    # Verify Declarative Business Knowledge Model (Subsystem 1)
    km = module.get_knowledge_model()
    assert km is not None
    assert len(km.vocabulary.terms) >= 2
    assert len(km.decision_frameworks) >= 1
    assert km.vocabulary.terms[0].name == "Food Cost Percentage"

    # Verify AI Knowledge Pack (Backward Compatibility)
    ai_pack = module.get_ai_knowledge_pack()
    assert len(ai_pack.vocabularies) >= 2


    # Verify Extension Points & Capabilities
    assert len(module.get_extension_points()) >= 1
    assert len(module.get_capabilities()) >= 2
    assert len(module.get_ui_navigation()) >= 3
