"""Declarative UI Metadata System for defining navigation, views, forms, and cards for frontends."""

from typing import Any

from pydantic import BaseModel, Field


class UINavigationItem(BaseModel):
    """Spec for a navigation menu item exposed by a module."""

    item_id: str
    label: str
    icon: str = "box"
    route: str
    order: int = 10


class UIViewSpec(BaseModel):
    """Spec for a declarative UI view/dashboard widget."""

    view_id: str
    module_id: str
    title: str
    view_type: str = "table"  # table, form, dashboard, kanban
    entity_type: str
    layout_schema: dict[str, Any] = Field(default_factory=dict)


class ModuleUIMetadataRegistry:
    """Registry managing UI Navigation and View declarations across modules."""

    def __init__(self) -> None:
        self._navigation: dict[str, list[UINavigationItem]] = {}
        self._views: dict[str, UIViewSpec] = {}

    def register_navigation(self, module_id: str, item: UINavigationItem) -> None:
        """Register a navigation item for a module."""
        if module_id not in self._navigation:
            self._navigation[module_id] = []
        self._navigation[module_id].append(item)

    def register_view(self, view: UIViewSpec) -> None:
        """Register a declarative view spec."""
        self._views[view.view_id] = view

    def get_navigation_tree(self) -> dict[str, list[UINavigationItem]]:
        """Fetch complete navigation tree for all active modules."""
        return self._navigation

    def list_views_for_module(self, module_id: str) -> list[UIViewSpec]:
        """Fetch view specs registered by a specific module."""
        return [v for v in self._views.values() if v.module_id == module_id]
