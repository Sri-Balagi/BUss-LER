from datetime import datetime
from abc import ABC, abstractmethod
from typing import Any
from pydantic import Field

from app.domain.intelligence.context import IntelligenceContext
from app.perception.models.observation import ExternalObservation, ObservationSourceType, UnifiedKnowledgeObject


class PerceptionContext(IntelligenceContext):
    """Context passed to Perception Engine and ObservationSources."""

    source_id: str | None = Field(default=None, description="Current observation source ID")
    limit: int = Field(default=50, description="Max observations to fetch")
    params: dict[str, Any] = Field(default_factory=dict, description="Source-specific fetch parameters")
    last_sync_at: datetime | None = Field(default=None, description="Timestamp of last successful perception sync")


class IObservationSource(ABC):
    """Interface implemented by any signal emitter into the Perception Engine."""

    @property
    @abstractmethod
    def source_id(self) -> str:
        """Globally unique identifier e.g. 'google_drive', 'gmail', 'slack'."""
        pass

    @property
    @abstractmethod
    def source_type(self) -> ObservationSourceType:
        """Type of source e.g. CONNECTOR, AGENT, SENSOR."""
        pass

    @abstractmethod
    async def observe(self, context: PerceptionContext) -> list[ExternalObservation]:
        """Fetch/emit raw external observations."""
        pass

    @abstractmethod
    def normalize(self, observation: ExternalObservation) -> UnifiedKnowledgeObject:
        """Normalize a raw external observation into a UnifiedKnowledgeObject."""
        pass
