from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class PluginMetadata(BaseModel):
    name: str
    version: str
    author: str
    description: str


class PluginDescriptor(BaseModel):
    plugin_id: str
    metadata: PluginMetadata
    capabilities: list[str]


class PluginPackage(ABC):
    @property
    @abstractmethod
    def descriptor(self) -> PluginDescriptor:
        pass

    @abstractmethod
    def get_capabilities(self) -> dict[str, Any]:
        """Returns capability factories provided by this plugin."""
        pass


class IPluginLoader(ABC):
    @abstractmethod
    async def load_plugin(self, path: str) -> PluginPackage:
        pass

    @abstractmethod
    async def unload_plugin(self, plugin_id: str) -> None:
        pass
