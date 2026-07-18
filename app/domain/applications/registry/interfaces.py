import abc
from typing import List, Optional

from app.domain.applications.base import ICognitiveApplication
from app.domain.applications.registry.models import ApplicationMetadata

class IApplicationRegistry(abc.ABC):
    """Registry for managing cognitive applications."""
    
    @abc.abstractmethod
    def register(self, application: ICognitiveApplication) -> None:
        """Register a new application."""
        pass

    @abc.abstractmethod
    def resolve(self, app_id: str) -> Optional[ICognitiveApplication]:
        """Resolve an application by its ID."""
        pass

    @abc.abstractmethod
    def get_all_metadata(self) -> List[ApplicationMetadata]:
        """Retrieve metadata for all registered applications."""
        pass
