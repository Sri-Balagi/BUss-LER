from abc import ABC, abstractmethod
from typing import Any, Dict
from app.shared.events.models import DomainEvent

class INotificationAdapter(ABC):
    """
    Adapter interface for dispatching notifications over specific transport protocols.
    """
    
    @abstractmethod
    async def dispatch(self, event: DomainEvent) -> None:
        """
        Dispatch the given domain event via the transport adapter.
        """
        pass
