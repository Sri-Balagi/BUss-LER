from typing import Any, Dict, List

from pydantic import BaseModel, Field

from app.runtime.registry.base import BaseRegistry


class PluginMetadata(BaseModel):
    id: str
    name: str
    description: str
    version: str = "1.0.0"
    author: str = "unknown"
    dependencies: List[str] = Field(default_factory=list)


class PluginRegistry(BaseRegistry[PluginMetadata]):
    """
    Registry for managing external Plugins.
    """

    def _deserialize_item(self, data: Dict[str, Any]) -> PluginMetadata:
        return PluginMetadata.model_validate(data)
