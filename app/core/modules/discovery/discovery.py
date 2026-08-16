"""Capability Discovery protocol for registering and querying module capabilities at runtime."""

from typing import Any

from pydantic import BaseModel, Field


class ModuleCapabilityDescriptor(BaseModel):
    """Machine-readable capability descriptor registered by a business module."""

    capability_id: str
    module_id: str
    name: str
    description: str
    category: str = "general"
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CapabilityDiscoveryRegistry:
    """Runtime registry exposing active capabilities across all installed modules."""

    def __init__(self) -> None:
        self._capabilities: dict[str, ModuleCapabilityDescriptor] = {}

    def register_capability(self, descriptor: ModuleCapabilityDescriptor) -> None:
        """Register a new capability descriptor."""
        self._capabilities[descriptor.capability_id] = descriptor

    def unregister_capability(self, capability_id: str) -> None:
        """Remove a capability registration."""
        self._capabilities.pop(capability_id, None)

    def get_capability(self, capability_id: str) -> ModuleCapabilityDescriptor | None:
        """Get capability descriptor by ID."""
        return self._capabilities.get(capability_id)

    def find_capabilities_by_category(self, category: str) -> list[ModuleCapabilityDescriptor]:
        """Find capabilities matching a specific category."""
        return [cap for cap in self._capabilities.values() if cap.category.lower() == category.lower()]

    def find_capabilities_by_module(self, module_id: str) -> list[ModuleCapabilityDescriptor]:
        """Find all capabilities exposed by a specific module."""
        return [cap for cap in self._capabilities.values() if cap.module_id == module_id]

    def list_all(self) -> list[ModuleCapabilityDescriptor]:
        """List all registered capabilities."""
        return list(self._capabilities.values())
