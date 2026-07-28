"""Module Manager and Dependency Resolver for orchestrating module lifecycles."""

import logging
from typing import Any

from app.core.modules.base import BaseModule
from app.core.modules.discovery.discovery import CapabilityDiscoveryRegistry
from app.core.modules.extension_points.extension_points import ExtensionPointRegistry
from app.core.modules.models import ModuleConfiguration, ModuleContext
from app.core.modules.registry import ModuleRegistry

logger = logging.getLogger(__name__)


class ModuleDependencyResolver:
    """Calculates topological execution order for module installations based on declared dependencies."""

    @staticmethod
    def resolve_installation_order(modules: list[BaseModule]) -> list[BaseModule]:
        """Return modules ordered so dependencies are initialized prior to dependents."""
        module_map = {m.manifest.module_id: m for m in modules}
        visited: set[str] = set()
        order: list[BaseModule] = []

        def visit(mod_id: str):
            if mod_id in visited:
                return
            visited.add(mod_id)
            mod = module_map.get(mod_id)
            if mod:
                for dep in mod.manifest.dependencies:
                    if dep in module_map:
                        visit(dep)
                order.append(mod)

        for m_id in module_map:
            visit(m_id)

        return order


class ModuleManager:
    """Master manager orchestrating module lifecycle, contracts, capability discovery, and health."""

    def __init__(
        self,
        registry: ModuleRegistry,
        capability_registry: CapabilityDiscoveryRegistry | None = None,
        extension_registry: ExtensionPointRegistry | None = None
    ) -> None:
        self.registry = registry
        self.capability_registry = capability_registry or CapabilityDiscoveryRegistry()
        self.extension_registry = extension_registry or ExtensionPointRegistry()
        self.services_broker: dict[str, Any] = {}

    def register_service_contract(self, contract_name: str, service_instance: Any) -> None:
        """Register a public contract service implementation."""
        self.services_broker[contract_name] = service_instance
        logger.info(f"Registered service contract: {contract_name}")

    def get_service_contract(self, contract_name: str) -> Any | None:
        """Retrieve a contract service implementation."""
        return self.services_broker.get(contract_name)

    async def install_module(self, module: BaseModule, context: ModuleContext) -> bool:
        """Install a module and register it in the registry."""
        self.registry.register_module(module)
        success = await module.install(context)
        if success:
            logger.info(f"Module {module.manifest.module_id} installed successfully.")
        return success

    async def initialize_module(self, module_id: str, context: ModuleContext) -> bool:
        """Initialize a module."""
        module = self.registry.get_module(module_id)
        if not module:
            raise ValueError(f"Module {module_id} not found")
        valid, missing = self.registry.validate_dependencies(module_id)
        if not valid:
            raise RuntimeError(f"Cannot initialize module {module_id}, missing dependencies: {missing}")

        return await module.initialize(context)

    async def enable_module(self, module_id: str, context: ModuleContext) -> bool:
        """Enable an initialized module."""
        module = self.registry.get_module(module_id)
        if not module:
            raise ValueError(f"Module {module_id} not found")
        return await module.enable(context)

    async def start_module(self, module_id: str, context: ModuleContext) -> bool:
        """Start an enabled module."""
        module = self.registry.get_module(module_id)
        if not module:
            raise ValueError(f"Module {module_id} not found")
        return await module.start(context)

    async def disable_module(self, module_id: str, context: ModuleContext) -> bool:
        """Disable a module."""
        module = self.registry.get_module(module_id)
        if not module:
            raise ValueError(f"Module {module_id} not found")
        return await module.disable(context)

    async def uninstall_module(self, module_id: str, context: ModuleContext) -> bool:
        """Uninstall a module."""
        module = self.registry.get_module(module_id)
        if not module:
            return False
        success = await module.uninstall(context)
        if success:
            self.registry.unregister_module(module_id)
        return success

    async def configure_module(self, module_id: str, config: ModuleConfiguration) -> bool:
        """Configure a module."""
        module = self.registry.get_module(module_id)
        if not module:
            return False
        return await module.configure(config)

    async def get_system_health(self) -> dict[str, Any]:
        """Perform system health check across all registered modules."""
        health_reports = {}
        for mod in self.registry.list_modules():
            health_reports[mod.manifest.module_id] = await mod.health_check()
        return health_reports
