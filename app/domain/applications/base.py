import abc
from typing import List, AsyncIterator, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.applications.worker.models import JobRecord

from app.domain.intelligence.capability import CapabilityType
from app.domain.applications.context.models import ApplicationContext
from app.domain.applications.registry.models import ApplicationMetadata

class ApplicationResponse:
    """Standardized response from an application."""
    def __init__(self, data: Any, metadata: dict = None):
        self.data = data
        self.metadata = metadata or {}

class ICognitiveApplication(abc.ABC):
    """Base interface for all cognitive applications."""
    
    @abc.abstractmethod
    def metadata(self) -> ApplicationMetadata:
        """Get the application metadata."""
        pass

    @abc.abstractmethod
    def supported_capabilities(self) -> List[CapabilityType]:
        """List of capabilities supported by this application."""
        pass

    @abc.abstractmethod
    async def execute(self, context: ApplicationContext) -> ApplicationResponse:
        """Execute the application returning a single response."""
        pass

    @abc.abstractmethod
    def health(self) -> bool:
        """Check application health."""
        pass

class IStreamingCognitiveApplication(ICognitiveApplication):
    """Interface for applications that stream responses."""
    
    @abc.abstractmethod
    async def execute_stream(self, context: ApplicationContext) -> AsyncIterator[ApplicationResponse]:
        """Execute the application asynchronously returning a stream."""
        pass

class IAsynchronousCognitiveApplication(ICognitiveApplication):
    """Interface for applications that support durable background execution (CQRS)."""
    
    @abc.abstractmethod
    async def submit_job(self, context: ApplicationContext) -> str:
        """Submit a job asynchronously and return a JobId."""
        pass
        
    @abc.abstractmethod
    async def get_job_status(self, job_id: str) -> 'JobRecord':
        """Retrieve the status of an asynchronous job."""
        pass


class ICognitiveOrchestrator(IAsynchronousCognitiveApplication):
    """Interface for components that orchestrate and dispatch other cognitive applications."""
    pass

