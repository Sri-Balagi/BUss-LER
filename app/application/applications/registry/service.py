import threading
from typing import Dict, List, Optional

from app.domain.applications.registry.interfaces import IApplicationRegistry
from app.domain.applications.base import ICognitiveApplication
from app.domain.applications.registry.models import ApplicationMetadata

class ApplicationRegistryService(IApplicationRegistry):
    def __init__(self):
        self._lock = threading.Lock()
        self._apps: Dict[str, ICognitiveApplication] = {}

    def register(self, application: ICognitiveApplication) -> None:
        metadata = application.metadata()
        with self._lock:
            self._apps[metadata.id] = application

    def resolve(self, app_id: str) -> Optional[ICognitiveApplication]:
        with self._lock:
            return self._apps.get(app_id)

    def get_all_metadata(self) -> List[ApplicationMetadata]:
        with self._lock:
            return [app.metadata() for app in self._apps.values()]
