from abc import ABC, abstractmethod
from typing import Any, Dict
from app.runtime.capabilities.models.request import CapabilityRequest

class IResourceAdapter(ABC):
    """
    Canonical adapter abstraction defining the boundary between BizOS and external systems.
    Adapters own all protocol-specific logic and physical resource communication.
    """
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize any internal structures before connection."""
        pass
        
    @abstractmethod
    async def connect(self) -> None:
        """Establish physical connections (e.g., DB sockets, HTTP sessions)."""
        pass
        
    @abstractmethod
    async def execute(self, request: CapabilityRequest) -> Dict[str, Any]:
        """
        Execute the protocol-specific operation mapped from the request.
        Returns raw protocol output.
        """
        pass
        
    @abstractmethod
    async def disconnect(self) -> None:
        """Safely close connections and release physical resources."""
        pass
        
    @abstractmethod
    async def cleanup(self) -> None:
        """Final cleanup of internal adapter state."""
        pass
