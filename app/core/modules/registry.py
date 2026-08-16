"""Module Registry for discovery, registration, metadata, and version management."""

import logging
from typing import Any

from app.core.modules.base import BaseModule
from app.core.modules.models import ModuleCategory, ModuleManifest, ModuleType

logger = logging.getLogger(__name__)


class ModuleRegistry:
    """Central registry for discovering, registering, and inspecting installed modules."""

    def __init__(self) -> None:
        self._modules: dict[str, BaseModule] = {}
        self._manifests: dict[str, ModuleManifest] = {}

    def register_module(self, module: BaseModule) -> None:
        """Register an instantiated module in the platform."""
        module_id = module.manifest.module_id
        if module_id in self._modules:
            logger.warning(f"Overwriting registration for module_id={module_id}")
        self._modules[module_id] = module
        self._manifests[module_id] = module.manifest
        logger.info(f"Registered module {module.manifest.name} ({module_id} v{module.manifest.version})")

    def unregister_module(self, module_id: str) -> None:
        """Unregister a module."""
        self._modules.pop(module_id, None)
        self._manifests.pop(module_id, None)
        logger.info(f"Unregistered module_id={module_id}")

    def get_module(self, module_id: str) -> BaseModule | None:
        """Fetch module instance by ID."""
        return self._modules.get(module_id)

    def get_manifest(self, module_id: str) -> ModuleManifest | None:
        """Fetch module manifest by ID."""
        return self._manifests.get(module_id)

    def list_modules(self, module_type: ModuleType | None = None, category: ModuleCategory | None = None) -> list[BaseModule]:
        """List modules filtered by type or category."""
        results = list(self._modules.values())
        if module_type:
            results = [m for m in results if m.manifest.module_type == module_type]
        if category:
            results = [m for m in results if m.manifest.category == category]
        return results

    def list_manifests(self) -> list[ModuleManifest]:
        """List all registered manifests."""
        return list(self._manifests.values())

    def validate_dependencies(self, module_id: str) -> tuple[bool, list[str]]:
        """Validate if all declared dependencies for a module are present."""
        manifest = self.get_manifest(module_id)
        if not manifest:
            return False, [f"Module {module_id} not found in registry"]

        missing = []
        for dep_id in manifest.dependencies:
            if dep_id not in self._modules:
                missing.append(dep_id)

        return len(missing) == 0, missing

    def collect_ai_metadata(self) -> dict[str, Any]:
        """Aggregate AI metadata, vocabularies, and knowledge packs from all active modules."""
        ai_vocabularies = []
        capabilities = []
        for m in self._modules.values():
            ai_vocabularies.extend(m.manifest.capabilities.ai_vocabularies)
            capabilities.extend(m.manifest.capabilities.provided_contracts)
        return {
            "registered_modules_count": len(self._modules),
            "ai_vocabularies": ai_vocabularies,
            "provided_contracts": capabilities
        }


_default_registry: ModuleRegistry | None = None


def get_module_registry() -> ModuleRegistry:
    """Fetch or initialize the singleton ModuleRegistry instance."""
    global _default_registry
    if _default_registry is None:
        _default_registry = ModuleRegistry()
    return _default_registry
