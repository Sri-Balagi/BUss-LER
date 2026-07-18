from abc import ABC, abstractmethod
from typing import Any, Dict

class Tool(ABC):
    """Base interface for all tools accessible by Intelligence Platform."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass
        
    @property
    @abstractmethod
    def parameters_schema(self) -> Dict[str, Any]:
        """JSON Schema representation of parameters."""
        pass
        
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        pass
