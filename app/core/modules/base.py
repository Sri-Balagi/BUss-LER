"""Abstract Base Module classes providing standard lifecycle implementation and hooks."""

from abc import ABC, abstractmethod
from typing import Any

from app.core.modules.lifecycle import ModuleLifecycleState, ModuleState
from app.core.modules.models import ModuleConfiguration, ModuleContext, ModuleManifest, ModuleType


class BaseModule(ABC):
    """Abstract Base Class for all BizOS Modules."""

    def __init__(self, manifest: ModuleManifest) -> None:
        self.manifest = manifest
        self.lifecycle = ModuleLifecycleState(module_id=manifest.module_id)
        self.configuration: ModuleConfiguration | None = None

    @abstractmethod
    async def install(self, context: ModuleContext) -> bool:
        """Perform database setup, schema migration, and initial resource creation."""
        pass

    @abstractmethod
    async def uninstall(self, context: ModuleContext) -> bool:
        """Clean up data structures and remove module metadata."""
        pass

    @abstractmethod
    async def initialize(self, context: ModuleContext) -> bool:
        """Load configuration, register services, and bind event handlers."""
        pass

    @abstractmethod
    async def configure(self, config: ModuleConfiguration) -> bool:
        """Apply runtime configuration updates."""
        pass

    @abstractmethod
    async def enable(self, context: ModuleContext) -> bool:
        """Enable active processing for this module."""
        pass

    @abstractmethod
    async def disable(self, context: ModuleContext) -> bool:
        """Disable active processing."""
        pass

    @abstractmethod
    async def start(self, context: ModuleContext) -> bool:
        """Start background jobs and runtime routines."""
        pass

    @abstractmethod
    async def stop(self, context: ModuleContext) -> bool:
        """Gracefully stop background jobs."""
        pass

    @abstractmethod
    async def pause(self, context: ModuleContext) -> bool:
        """Temporarily pause module execution."""
        pass

    @abstractmethod
    async def resume(self, context: ModuleContext) -> bool:
        """Resume paused module execution."""
        pass

    @abstractmethod
    async def upgrade(self, context: ModuleContext, target_version: str) -> bool:
        """Upgrade module version and data schemas."""
        pass

    @abstractmethod
    async def rollback(self, context: ModuleContext, target_version: str) -> bool:
        """Rollback to a previous module version."""
        pass

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Check system health status of this module."""
        pass

    @abstractmethod
    async def shutdown(self) -> bool:
        """Release all allocated resources and close connections."""
        pass


class BusinessModule(BaseModule):
    """Base class for Business Modules (both Vertical and Horizontal)."""

    async def install(self, context: ModuleContext) -> bool:
        self.lifecycle.transition_to(ModuleState.INSTALLED, "Installed successfully")
        return True

    async def uninstall(self, context: ModuleContext) -> bool:
        self.lifecycle.transition_to(ModuleState.UNINSTALLED, "Uninstalled successfully")
        return True

    async def initialize(self, context: ModuleContext) -> bool:
        self.lifecycle.transition_to(ModuleState.INITIALIZED, "Initialized successfully")
        return True

    async def configure(self, config: ModuleConfiguration) -> bool:
        self.configuration = config
        return True

    async def enable(self, context: ModuleContext) -> bool:
        self.lifecycle.transition_to(ModuleState.ENABLED, "Enabled successfully")
        return True

    async def disable(self, context: ModuleContext) -> bool:
        self.lifecycle.transition_to(ModuleState.DISABLED, "Disabled successfully")
        return True

    async def start(self, context: ModuleContext) -> bool:
        self.lifecycle.transition_to(ModuleState.ACTIVE, "Started successfully")
        return True

    async def stop(self, context: ModuleContext) -> bool:
        self.lifecycle.transition_to(ModuleState.ENABLED, "Stopped successfully")
        return True

    async def pause(self, context: ModuleContext) -> bool:
        self.lifecycle.transition_to(ModuleState.PAUSED, "Paused execution")
        return True

    async def resume(self, context: ModuleContext) -> bool:
        self.lifecycle.transition_to(ModuleState.ACTIVE, "Resumed execution")
        return True

    async def upgrade(self, context: ModuleContext, target_version: str) -> bool:
        self.manifest.version = target_version
        return True

    async def rollback(self, context: ModuleContext, target_version: str) -> bool:
        self.manifest.version = target_version
        return True

    async def health_check(self) -> dict[str, Any]:
        return {
            "module_id": self.manifest.module_id,
            "status": self.lifecycle.current_state.value,
            "healthy": self.lifecycle.current_state in [ModuleState.ACTIVE, ModuleState.ENABLED, ModuleState.INITIALIZED]
        }

    async def shutdown(self) -> bool:
        self.lifecycle.transition_to(ModuleState.UNINSTALLED, "Shutdown complete")
        return True

    def get_knowledge_model(self) -> Any | None:
        """Expose Subsystem 1 static BusinessKnowledgeModel declaration."""
        return None

    def list_agent_templates(self) -> list[Any]:
        """Discover all default AgentTemplate definitions shipped with this module."""
        km = self.get_knowledge_model()
        if km and getattr(km, "agent_templates", None):
            return km.agent_templates
        return []

    def create_agent_from_template(self, template_id_or_name: str, override_name: str | None = None) -> dict[str, Any]:
        """Instantiate a digital workforce agent specification from a module template."""
        templates = self.list_agent_templates()
        target = None
        for t in templates:
            t_id = getattr(t, "template_id", None) or getattr(t, "name", "").lower().replace(" ", "_")
            if t_id == template_id_or_name or getattr(t, "name", "") == template_id_or_name:
                target = t
                break
        if not target and templates:
            target = templates[0]
        if not target:
            return {"name": override_name or "Default Module Agent", "capabilities": []}
        return {
            "template_id": getattr(target, "template_id", None) or getattr(target, "name", "").lower().replace(" ", "_"),
            "name": override_name or getattr(target, "name", "Module Agent"),
            "role": getattr(target, "role", "Specialist"),
            "description": getattr(target, "description", ""),
            "capabilities": getattr(target, "capabilities", []),
            "default_permissions": getattr(target, "default_permissions", []),
            "default_workflows": getattr(target, "default_workflows", []),
        }



class VerticalModule(BusinessModule):
    """Base class for Vertical Industry Business Modules (e.g. Restaurant, Healthcare, Retail)."""

    def __init__(self, manifest: ModuleManifest) -> None:
        manifest.module_type = ModuleType.VERTICAL
        super().__init__(manifest)


class HorizontalModule(BusinessModule):
    """Base class for Horizontal Functional Business Modules (e.g. CRM, HR, Accounting)."""

    def __init__(self, manifest: ModuleManifest) -> None:
        manifest.module_type = ModuleType.HORIZONTAL
        super().__init__(manifest)


class DomainModule(BusinessModule):
    """Base class for sub-domain modules within a larger business ecosystem."""
    pass
