from abc import ABC, abstractmethod
from typing import Any, Dict


class IRegistryBus(ABC):
    """
    Interface for broadcasting registry lifecycle events to the broader system.
    Allows other components to react when items are registered or unregistered.
    """

    @abstractmethod
    async def publish_event(self, topic: str, payload: Dict[str, Any]) -> None:
        """
        Publishes an event to the underlying bus.
        Topics generally follow the format: 'registry.{registry_name}.{event_type}'
        """
        pass
