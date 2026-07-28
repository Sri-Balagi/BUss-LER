"""Extension Points framework enabling modules to extend other modules without modifying source code."""

from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, Field


class ExtensionHook(BaseModel):
    """Metadata describing a hook registered at an extension point."""

    hook_id: str
    target_point_id: str
    source_module_id: str
    description: str = ""
    priority: int = 100  # Lower numbers execute first


class ModuleExtensionPoint(BaseModel):
    """Metadata describing an extension point exposed by a module."""

    point_id: str
    module_id: str
    name: str
    description: str
    accepted_input_schema: dict[str, Any] = Field(default_factory=dict)


class ExtensionPointRegistry:
    """Registry managing active extension points and interceptor hooks across modules."""

    def __init__(self) -> None:
        self._points: dict[str, ModuleExtensionPoint] = {}
        self._hooks: dict[str, list[tuple[ExtensionHook, Callable[..., Any]]]] = {}

    def register_point(self, point: ModuleExtensionPoint) -> None:
        """Expose a new extension point."""
        self._points[point.point_id] = point
        if point.point_id not in self._hooks:
            self._hooks[point.point_id] = []

    def register_hook(self, hook: ExtensionHook, handler: Callable[..., Any]) -> None:
        """Register a handler hook at a target extension point."""
        if hook.target_point_id not in self._hooks:
            self._hooks[hook.target_point_id] = []
        self._hooks[hook.target_point_id].append((hook, handler))
        # Sort by priority ascending
        self._hooks[hook.target_point_id].sort(key=lambda x: x[0].priority)

    async def execute_hooks(self, point_id: str, context_data: dict[str, Any]) -> dict[str, Any]:
        """Execute all registered interceptor hooks for an extension point sequentially."""
        current_data = dict(context_data)
        if point_id in self._hooks:
            for _, handler in self._hooks[point_id]:
                res = handler(current_data)
                if hasattr(res, "__await__"):
                    res = await res
                if isinstance(res, dict):
                    current_data.update(res)
        return current_data

    def list_points(self) -> list[ModuleExtensionPoint]:
        """List all registered extension points."""
        return list(self._points.values())
