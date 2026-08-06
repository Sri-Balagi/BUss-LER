from typing import Dict, List, Optional
import structlog

from app.perception.sources.interface import IObservationSource

logger = structlog.get_logger(__name__)


class ObservationSourceRegistry:
    """Registry manager for resolution of observation sources."""

    def __init__(self) -> None:
        self._sources: Dict[str, IObservationSource] = {}

    def register(self, source: IObservationSource) -> None:
        self._sources[source.source_id] = source
        logger.info("Registered observation source", source_id=source.source_id, source_type=source.source_type.value)

    def get_source(self, source_id: str) -> Optional[IObservationSource]:
        return self._sources.get(source_id)

    def list_sources(self) -> List[IObservationSource]:
        return list(self._sources.values())
