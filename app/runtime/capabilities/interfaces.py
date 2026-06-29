from abc import ABC, abstractmethod
from app.runtime.capabilities.context import CapabilityContext
from app.runtime.capabilities.models.request import CapabilityRequest
from app.runtime.capabilities.models.result import CapabilityResult
from app.runtime.capabilities.models.specification import CapabilitySpecification

class ICapability(ABC):
    """
    Canonical execution primitive for capabilities.
    Does NOT contain external protocol logic (delegates to ResourceAdapter).
    """
    
    @abstractmethod
    async def initialize(self, context: CapabilityContext) -> None:
        """Initialize the capability within a restricted execution context."""
        pass
        
    @abstractmethod
    async def validate(self, request: CapabilityRequest) -> None:
        """Validate the incoming request against the capability's requirements."""
        pass
        
    @abstractmethod
    async def execute(self, request: CapabilityRequest) -> CapabilityResult:
        """Execute the operation by delegating to adapters and transforming the result."""
        pass
        
    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up capability resources and underlying adapters."""
        pass

class ICapabilityFactory(ABC):
    """
    Instantiates capabilities.
    """
    @abstractmethod
    def create(self, spec: CapabilitySpecification) -> ICapability:
        """Create a capability instance from a specification."""
        pass
