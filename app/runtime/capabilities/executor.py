from abc import ABC, abstractmethod
from typing import Optional
from app.runtime.capabilities.models.request import CapabilityRequest
from app.runtime.capabilities.models.result import CapabilityResult
from app.runtime.capabilities.context import CapabilityContext

class ICapabilityExecutor(ABC):
    """
    Facade for Agents to execute capabilities without knowing about 
    the CapabilityManager, Registry, or Middleware.
    """
    @abstractmethod
    async def execute_capability(
        self, 
        request: CapabilityRequest, 
        context: Optional[CapabilityContext] = None
    ) -> CapabilityResult:
        pass
