"""AI Tool Layer exposing connector capabilities as agent-callable tools."""
from __future__ import annotations
import logging
from typing import Any
from pydantic import BaseModel, Field
from app.connectors.exceptions.errors import ToolNotFoundError

logger = logging.getLogger(__name__)


class ToolParameter(BaseModel):
    name: str
    type: str  # "string", "integer", "boolean", "object"
    description: str
    required: bool = True
    default: Any = None


class ConnectorTool(BaseModel):
    """Declarative definition of a tool callable by AI agents."""

    tool_id: str  # e.g., "github.create_issue"
    connector_id: str
    capability_id: str
    name: str
    description: str
    parameters: list[ToolParameter] = Field(default_factory=list)
    returns_description: str = ""


class ToolRegistry:
    """Registry bridging Connector operations to AI Agent tool selection."""

    def __init__(self) -> None:
        self._tools: dict[str, ConnectorTool] = {}

    def register_tool(self, tool: ConnectorTool) -> None:
        self._tools[tool.tool_id] = tool
        logger.info("Tool registered: %s for connector %s", tool.tool_id, tool.connector_id)

    def get_tool(self, tool_id: str) -> ConnectorTool:
        tool = self._tools.get(tool_id)
        if not tool:
            raise ToolNotFoundError(f"Tool {tool_id!r} not found", connector_id="")
        return tool

    def list_by_connector(self, connector_id: str) -> list[ConnectorTool]:
        return [t for t in self._tools.values() if t.connector_id == connector_id]

    def list_all(self) -> list[ConnectorTool]:
        return list(self._tools.values())
