import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel

from app.runtime.registry.registry_bus import IRegistryBus
from app.runtime.registry.store import IRegistryStore
from app.runtime.registry.sync import RegistrySnapshot

logger = logging.getLogger(__name__)

T = TypeVar("T")


class BaseRegistry(ABC, Generic[T]):
    """
    Advanced foundation for all BizOS Registries.
    Provides standardized storage, broadcasting, lifecycle hooks, and synchronization.
    """

    def __init__(
        self, 
        name: str, 
        store: IRegistryStore[T], 
        bus: Optional[IRegistryBus] = None
    ) -> None:
        self.name = name
        self.store = store
        self.bus = bus

    # ── Hooks & Validation ───────────────────────────────────────────────────
    
    def validate_item(self, item: T) -> None:
        """
        Validates the item before registration.
        Raises ValueError if invalid. Subclasses should override.
        """
        pass

    async def on_register(self, item_id: str, item: T) -> None:
        """Hook called immediately after an item is successfully registered."""
        pass

    async def on_unregister(self, item_id: str, item: T) -> None:
        """Hook called immediately after an item is successfully unregistered."""
        pass

    # ── Core Operations ──────────────────────────────────────────────────────

    async def register(self, item_id: str, item: T) -> None:
        """Registers a new item in the registry."""
        self.validate_item(item)
        
        await self.store.set(item_id, item)
        logger.info(f"[{self.name}] Registered item: {item_id}")
        
        await self.on_register(item_id, item)
        
        if self.bus:
            await self.bus.publish_event(
                topic=f"registry.{self.name}.registered",
                payload={"item_id": item_id}
            )

    async def unregister(self, item_id: str) -> bool:
        """Removes an item from the registry."""
        item = await self.store.get(item_id)
        if not item:
            return False
            
        success = await self.store.delete(item_id)
        if success:
            logger.info(f"[{self.name}] Unregistered item: {item_id}")
            await self.on_unregister(item_id, item)
            
            if self.bus:
                await self.bus.publish_event(
                    topic=f"registry.{self.name}.unregistered",
                    payload={"item_id": item_id}
                )
        return success

    async def get(self, item_id: str) -> Optional[T]:
        """Retrieves an item by ID."""
        return await self.store.get(item_id)

    async def list_all(self) -> List[T]:
        """Retrieves all registered items."""
        return await self.store.list_all()

    # ── Synchronization ──────────────────────────────────────────────────────

    def _serialize_item(self, item: T) -> Dict[str, Any]:
        """Serializes an item for snapshotting. Default assumes Pydantic BaseModel."""
        if isinstance(item, BaseModel):
            return item.model_dump(mode="json")
        elif hasattr(item, "to_dict"):
            return item.to_dict() # type: ignore
        else:
            raise NotImplementedError(f"[{self.name}] Cannot serialize item: {type(item)}")

    @abstractmethod
    def _deserialize_item(self, data: Dict[str, Any]) -> T:
        """Deserializes an item from a snapshot. Subclasses must implement."""
        pass

    async def export_snapshot(self) -> RegistrySnapshot:
        """Creates a point-in-time snapshot of the entire registry."""
        items = await self.list_all()
        serialized_items = [self._serialize_item(i) for i in items]
        
        return RegistrySnapshot(
            registry_name=self.name,
            items=serialized_items
        )

    async def import_snapshot(self, snapshot: RegistrySnapshot, clear_existing: bool = False) -> None:
        """Imports a snapshot into the registry."""
        if snapshot.registry_name != self.name:
            raise ValueError(f"Snapshot registry name mismatch: {snapshot.registry_name} != {self.name}")
            
        if clear_existing:
            await self.store.clear()
            
        for idx, item_data in enumerate(snapshot.items):
            try:
                item = self._deserialize_item(item_data)
                # By convention, items usually have an 'id' or 'name' field
                item_id = item_data.get("id") or item_data.get("name") or f"imported_{idx}"
                await self.register(item_id, item)
            except Exception as e:
                logger.error(f"[{self.name}] Failed to import item {idx}: {e}")
                raise
