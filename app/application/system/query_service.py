from typing import Any

from app.runtime.kernel.interfaces import IRuntimeManager
from app.runtime.registry.base import BaseRegistry


class SystemQueryService:
    """
    Application Service for handling read-only queries about the system state.
    Provides a decoupled boundary between the API and the underlying Kernel / Registries.
    """

    def __init__(
        self,
        runtime_manager: IRuntimeManager,
        tool_registry: BaseRegistry[Any],
        workflow_registry: BaseRegistry[Any],
    ):
        self.runtime_manager = runtime_manager

        # Centralized mapping of available registries for queries
        self._registries: dict[str, BaseRegistry[Any]] = {
            "ToolRegistry": tool_registry,
            "WorkflowRegistry": workflow_registry,
        }

    async def list_active_workflows(self) -> list[dict[str, Any]]:
        """
        Retrieves a list of currently active workflows/processes from the Kernel.
        """
        # In a fully realized system, runtime_manager.list_processes() would exist.
        # Since IRuntimeManager doesn't expose it directly in MVP, we might need
        # to query the ProcessManager or ProcessTable.
        # Let's check what IRuntimeManager actually exposes. For now, we return empty list if not implemented.
        try:
            # Assuming IRuntimeManager exposes process_manager which exposes process_table
            # or we just return an empty list for MVP since we don't have real workflows running yet.
            if hasattr(self.runtime_manager, "process_manager"):
                processes = self.runtime_manager.process_manager.list_processes() # type: ignore
                return [{"id": str(p.pid), "status": p.state.name, "started": p.start_time.isoformat() if p.start_time else None} for p in processes]
        except AttributeError:
            pass

        return []

    async def list_registry_items(self, registry_name: str) -> list[dict[str, Any]]:
        """
        Retrieves all items from a specified registry.
        """
        registry = self._registries.get(registry_name)
        if not registry:
            raise ValueError(f"Registry not found: {registry_name}")

        items = await registry.list_all()

        # Serialize based on whether the items are Pydantic models or plain objects
        serialized = []
        for item in items:
            if hasattr(item, "model_dump"):
                serialized.append(item.model_dump())
            elif hasattr(item, "to_dict"):
                serialized.append(item.to_dict()) # type: ignore
            else:
                # Basic fallback
                serialized.append(
                    {
                        "id": getattr(item, "id", str(item)),
                        "name": getattr(item, "name", str(item)),
                        "type": getattr(item, "type", "Unknown"),
                    }
                )

        return serialized

    async def get_memory_status(self) -> dict[str, Any]:
        """
        Retrieves the status of the memory subsystem.
        """
        # Memory subsystem is deferred to Wave 4.
        return {
            "status": "Not Yet Available",
            "message": "Memory subsystem is pending implementation (Wave 4)."
        }
