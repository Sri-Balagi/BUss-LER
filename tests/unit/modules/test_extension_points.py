"""Unit tests for Capability Discovery, Extension Points, Business Rules Engine, and Platform Services."""

import pytest

from app.core.modules.discovery.discovery import (
    CapabilityDiscoveryRegistry,
    ModuleCapabilityDescriptor,
)
from app.core.modules.extension_points.extension_points import (
    ExtensionHook,
    ExtensionPointRegistry,
    ModuleExtensionPoint,
)
from app.core.modules.services.rules_engine import BusinessRule, BusinessRuleEngine
from app.core.modules.services.ui_metadata import ModuleUIMetadataRegistry, UINavigationItem


def test_capability_discovery():
    reg = CapabilityDiscoveryRegistry()
    cap = ModuleCapabilityDescriptor(
        capability_id="rest_order_cap",
        module_id="bizos.modules.restaurant.v1",
        name="Order Processing",
        description="Processes restaurant orders",
        category="restaurant"
    )
    reg.register_capability(cap)

    assert reg.get_capability("rest_order_cap") is not None
    found = reg.find_capabilities_by_category("restaurant")
    assert len(found) == 1
    assert found[0].capability_id == "rest_order_cap"


@pytest.mark.asyncio
async def test_extension_point_hooks():
    reg = ExtensionPointRegistry()
    point = ModuleExtensionPoint(
        point_id="order_discount_point",
        module_id="bizos.modules.restaurant.v1",
        name="Discount Extension Point",
        description="Alters total price"
    )
    reg.register_point(point)

    hook = ExtensionHook(
        hook_id="loyalty_discount",
        target_point_id="order_discount_point",
        source_module_id="bizos.modules.loyalty.v1",
        priority=10
    )

    def apply_discount(data: dict):
        data["total"] = data.get("total", 100.0) - 10.0
        return data

    reg.register_hook(hook, apply_discount)

    res = await reg.execute_hooks("order_discount_point", {"total": 100.0})
    assert res["total"] == 90.0


def test_business_rules_engine():
    engine = BusinessRuleEngine()
    rule = BusinessRule(
        rule_id="min_order_total",
        module_id="bizos.modules.restaurant.v1",
        name="Minimum Order Total",
        description="Order total must be at least $5.00",
        entity_type="Order"
    )

    def check_min_total(order_data: dict) -> bool:
        return order_data.get("amount", 0.0) >= 5.0

    engine.register_rule(rule, check_min_total)

    valid, violations = engine.evaluate_rules("Order", {"amount": 10.0})
    assert valid is True

    valid_invalid, violations_invalid = engine.evaluate_rules("Order", {"amount": 2.0})
    assert valid_invalid is False
    assert len(violations_invalid) == 1
