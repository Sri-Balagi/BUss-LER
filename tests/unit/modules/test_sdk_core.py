"""Unit tests for BizOS Module SDK Core, Registry, Lifecycle, and Shared Kernel."""

from decimal import Decimal

import pytest

from app.core.modules.base import BusinessModule
from app.core.modules.kernel.kernel_models import Customer, Money
from app.core.modules.lifecycle import ModuleState
from app.core.modules.manager import ModuleDependencyResolver, ModuleManager
from app.core.modules.models import ModuleCategory, ModuleContext, ModuleManifest, ModuleType
from app.core.modules.registry import ModuleRegistry


class DummyModule(BusinessModule):
    def __init__(self, mod_id: str, deps: list[str] | None = None) -> None:
        manifest = ModuleManifest(
            module_id=mod_id,
            name=f"Dummy Module {mod_id}",
            description="Test dummy module",
            version="1.0.0",
            module_type=ModuleType.VERTICAL,
            category=ModuleCategory.RESTAURANT,
            dependencies=deps or []
        )
        super().__init__(manifest)


@pytest.mark.asyncio
async def test_shared_kernel_money():
    m1 = Money(amount=Decimal("15.50"))
    m2 = Money(amount=Decimal("4.50"))
    total = m1.add(m2)
    assert total.amount == Decimal("20.00")
    mult = total.multiply(2)
    assert mult.amount == Decimal("40.00")


@pytest.mark.asyncio
async def test_module_lifecycle_and_registry():
    registry = ModuleRegistry()
    manager = ModuleManager(registry=registry)

    mod = DummyModule("bizos.modules.test.v1")
    ctx = ModuleContext(tenant_id="tenant_123")

    # Install
    assert await manager.install_module(mod, ctx) is True
    assert registry.get_module("bizos.modules.test.v1") is not None
    assert mod.lifecycle.current_state == ModuleState.INSTALLED

    # Initialize
    assert await manager.initialize_module("bizos.modules.test.v1", ctx) is True
    assert mod.lifecycle.current_state == ModuleState.INITIALIZED

    # Enable
    assert await manager.enable_module("bizos.modules.test.v1", ctx) is True
    assert mod.lifecycle.current_state == ModuleState.ENABLED

    # Health check
    health = await manager.get_system_health()
    assert health["bizos.modules.test.v1"]["healthy"] is True

    # Uninstall
    assert await manager.uninstall_module("bizos.modules.test.v1", ctx) is True
    assert registry.get_module("bizos.modules.test.v1") is None


def test_dependency_resolver():
    mod_a = DummyModule("mod.a")
    mod_b = DummyModule("mod.b", deps=["mod.a"])
    mod_c = DummyModule("mod.c", deps=["mod.b"])

    ordered = ModuleDependencyResolver.resolve_installation_order([mod_c, mod_a, mod_b])
    ordered_ids = [m.manifest.module_id for m in ordered]

    assert ordered_ids.index("mod.a") < ordered_ids.index("mod.b")
    assert ordered_ids.index("mod.b") < ordered_ids.index("mod.c")
