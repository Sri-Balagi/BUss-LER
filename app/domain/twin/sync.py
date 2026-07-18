import abc
from uuid import UUID
from app.domain.intelligence.context import IntelligenceContext

class ITwinSynchronizer(abc.ABC):
    """Base strategy interface for synchronizing twins from source events."""
    
    @abc.abstractmethod
    async def synchronize(self, context: IntelligenceContext, entity_id: UUID) -> None:
        pass


class RealTimeSynchronization(ITwinSynchronizer):
    """Synchronizes immediately upon receiving Domain Events."""
    async def synchronize(self, context: IntelligenceContext, entity_id: UUID) -> None:
        # In a real implementation, this would fetch from BKG/Memory immediately
        pass


class EventualSynchronization(ITwinSynchronizer):
    """Batches state mutations for periodic updates."""
    async def synchronize(self, context: IntelligenceContext, entity_id: UUID) -> None:
        pass


class SnapshotRebuild(ITwinSynchronizer):
    """Re-calculates Twin state entirely from historical event sourcing."""
    async def synchronize(self, context: IntelligenceContext, entity_id: UUID) -> None:
        pass
