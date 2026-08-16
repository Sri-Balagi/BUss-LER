from typing import Any

from pydantic import BaseModel, Field

from app.runtime.registry.base import BaseRegistry


class ToolMetadata(BaseModel):
    id: str
    name: str
    description: str
    version: str = "1.0.0"
    permissions: list[str] = Field(default_factory=list)
    risk_level: str = "LOW"
    human_approval_required: bool = False


class ToolRegistry(BaseRegistry[ToolMetadata]):
    """
    Registry for managing Tools (including MCP tools).
    """

    def _deserialize_item(self, data: dict[str, Any]) -> ToolMetadata:
        return ToolMetadata.model_validate(data)
