import structlog
from typing import Callable

from app.models.events import MemoryLifecycleEvent
from app.workers.memory_worker import MemoryProcessingWorker
from app.services.memory_service import AbstractMemoryService

logger = structlog.get_logger(__name__)


class MemoryCreatedHandler:
    """
    Handler for MemoryLifecycleEvent (CREATED).
    Orchestrates the MemoryProcessingWorker.
    """

    def __init__(self, worker: MemoryProcessingWorker):
        self._worker = worker

    async def handle(self, event: MemoryLifecycleEvent) -> None:
        """Executes the handler logic."""
        logger.info(
            "MemoryCreatedHandler invoked", 
            event_id=str(event.event_id),
            correlation_id=event.correlation_id,
        )
        await self._worker.handle_event(event)
