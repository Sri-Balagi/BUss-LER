from uuid import UUID

from app.application.intelligence.kernel import IntelligenceKernel
from app.application.twin.service import DigitalTwinService
from app.domain.intelligence.context import IntelligenceContext
from app.domain.twin.events import TwinStateUpdated
from app.domain.twin.sync import ITwinSynchronizer


class TwinSyncOrchestrator:
    """Orchestrates events from BKG/Memory to update the Twin via the designated strategy."""

    def __init__(self, synchronizer: ITwinSynchronizer, twin_service: DigitalTwinService, kernel: IntelligenceKernel):
        self._synchronizer = synchronizer
        self._twin_service = twin_service
        self._kernel = kernel

    async def handle_bkg_entity_updated(self, context: IntelligenceContext, entity_id: UUID, new_properties: dict):
        # 1. Ensure Twin exists or create it
        twin = await self._twin_service.get_twin(context, entity_id)
        if not twin:
            twin = await self._twin_service.create_twin(context, entity_id, "Unknown")

        # 2. Delegate to the synchronization strategy
        await self._synchronizer.synchronize(context, entity_id)

        # 3. For RealTime, we apply it directly
        updated_twin = await self._twin_service.update_twin_properties(context, entity_id, new_properties)
        if updated_twin:
            # 4. Emit TwinStateUpdated through the Intelligence Kernel EventRouter
            event = TwinStateUpdated(
                correlation_id=context.correlation_id,
                entity_id=updated_twin.entity_id,
                tenant_id=updated_twin.tenant_id,
                version=updated_twin.version,
                changes=new_properties
            )
            await self._kernel.event_router.publish(event)
