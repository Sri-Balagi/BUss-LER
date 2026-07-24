import abc
from uuid import UUID

from app.domain.intelligence.provider import IIntelligenceProvider
from app.domain.twin.models import DigitalTwinState, TwinSnapshot


class ITwinProvider(IIntelligenceProvider):
    """Abstracts persistence and retrieval of Digital Twins."""

    @abc.abstractmethod
    async def get_twin(self, tenant_id: UUID, entity_id: UUID) -> DigitalTwinState | None:
        pass

    @abc.abstractmethod
    async def save_twin(self, twin: DigitalTwinState) -> None:
        pass

    @abc.abstractmethod
    async def get_snapshot(self, snapshot_id: UUID) -> TwinSnapshot | None:
        pass

    @abc.abstractmethod
    async def save_snapshot(self, snapshot: TwinSnapshot) -> None:
        pass
