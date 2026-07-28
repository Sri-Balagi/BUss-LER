"""AI Agent Capability Hooks for registering module reasoning rules and agent tools."""

from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, Field


class AgentToolSpec(BaseModel):
    """Specification for a tool exposed by a module to AI Agents."""

    tool_id: str
    module_id: str
    name: str
    description: str
    parameters_schema: dict[str, Any] = Field(default_factory=dict)


class AIAgentHooksRegistry:
    """Registry managing AI agent tool hooks and multi-agent collaboration specs across modules."""

    def __init__(self) -> None:
        self._tools: dict[str, tuple[AgentToolSpec, Callable[..., Any]]] = {}

    def register_tool(self, spec: AgentToolSpec, handler: Callable[..., Any]) -> None:
        """Register an AI agent tool provided by a module."""
        self._tools[spec.tool_id] = (spec, handler)

    def list_agent_tools(self) -> list[AgentToolSpec]:
        """List all tools exposed to AI Agents."""
        return [spec for spec, _ in self._tools.values()]

    async def execute_tool(self, tool_id: str, arguments: dict[str, Any]) -> Any:
        """Execute an AI agent tool."""
        if tool_id not in self._tools:
            raise ValueError(f"Tool {tool_id} not registered")
        _, handler = self._tools[tool_id]
        res = handler(arguments)
        if hasattr(res, "__await__"):
            res = await res
        return res
