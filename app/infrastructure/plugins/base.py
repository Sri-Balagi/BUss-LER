"""Business Plugin Framework for domain isolation in BizOS Core."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class IBusinessPlugin(ABC):
    """Abstract base interface for domain business plugins."""

    @property
    @abstractmethod
    def plugin_name(self) -> str:
        """Name of the business domain plugin (e.g. 'restaurant')."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin semver version."""
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """Lifecycle hook executed when plugin is loaded into BizOS."""
        pass

    @abstractmethod
    def get_knowledge_documents(self) -> List[Dict[str, Any]]:
        """Return business domain knowledge documents for ingestion."""
        pass

    @abstractmethod
    def get_initial_digital_twin_properties(self) -> Dict[str, Any]:
        """Return initial domain entity properties for Digital Twin sync."""
        pass

    @abstractmethod
    def get_crisis_scenarios(self) -> List[Dict[str, Any]]:
        """Return domain crisis goals / scenarios for simulation."""
        pass


class BusinessPluginRegistry:
    """Registry managing business domain plugins."""

    def __init__(self):
        self._plugins: Dict[str, IBusinessPlugin] = {}

    def register(self, plugin: IBusinessPlugin) -> None:
        self._plugins[plugin.plugin_name] = plugin

    def get_plugin(self, name: str) -> Optional[IBusinessPlugin]:
        return self._plugins.get(name)

    def list_plugins(self) -> List[str]:
        return list(self._plugins.keys())
