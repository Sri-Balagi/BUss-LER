from typing import Optional
from uuid import UUID, uuid4
import structlog

from app.domain.twin.events import TwinStateUpdated
from app.domain.twin.models import DigitalTwinState, TwinLifecycleStatus
from app.domain.twin.sync import RealTimeSynchronization
from app.domain.twin.sync_engine import DigitalTwinSyncEngine
from app.shared.events.models import BusinessStateChangeEvent

logger = structlog.get_logger(__name__)


class TwinSynchronizationService(RealTimeSynchronization):
    """
    Subscribes to BusinessStateChangeEvent on the EventBus.
    Translates state changes into live DigitalTwinState mutations and emits TwinStateUpdated events.
    """

    def __init__(
        self,
        twin_provider: Optional[object] = None,
        event_bus: Optional[object] = None,
    ) -> None:
        self.twin_provider = twin_provider
        self.event_bus = event_bus

    async def handle_business_state_change(self, event: BusinessStateChangeEvent) -> None:
        """Handle incoming BusinessStateChangeEvent from Perception Engine."""
        logger.info("TwinSynchronizationService processing BusinessStateChangeEvent", change_id=event.change_id)

        tenant_uuid = UUID(event.tenant_id) if event.tenant_id and len(event.tenant_id) == 36 else uuid4()
        entity_uuid = (
            UUID(event.affected_entity_ids[0])
            if event.affected_entity_ids and len(event.affected_entity_ids[0]) == 36
            else uuid4()
        )

        # Retrieve or instantiate Twin state
        twin: Optional[DigitalTwinState] = None
        if self.twin_provider:
            try:
                twin = await self.twin_provider.get_twin(tenant_uuid, entity_uuid)
            except Exception as e:
                logger.warning("Error fetching twin from provider", error=str(e))

        if twin is None:
            sync_engine = DigitalTwinSyncEngine(
                tenant_id=tenant_uuid,
                entity_id=entity_uuid,
                entity_type="BUSINESS_ENTITY",
            )
            twin = sync_engine.get_state()
        else:
            sync_engine = DigitalTwinSyncEngine(
                tenant_id=twin.tenant_id,
                entity_id=twin.entity_id,
                entity_type=twin.entity_type,
            )
            sync_engine.active_twin = twin

        # Prepare property mutations derived from business state change
        updates: dict = {
            "last_perceived_event": ", ".join(event.business_event_types) if event.business_event_types else "NONE",
            "last_perceived_connector": event.source_connector,
            "last_perceived_change_id": event.change_id,
        }

        if "APPROVAL_RECEIVED" in event.business_event_types:
            updates["approval_status"] = "APPROVED"
        elif "CONTRACT_SIGNED" in event.business_event_types:
            updates["contract_status"] = "EXECUTED"
        elif "PROPOSAL_CREATED" in event.business_event_types:
            updates["proposal_status"] = "CREATED"

        sync_engine.batch_update_properties(updates)
        updated_twin = sync_engine.get_state()

        if self.twin_provider:
            try:
                await self.twin_provider.save_twin(updated_twin)
            except Exception as e:
                logger.warning("Error saving twin to provider", error=str(e))

        # Publish TwinStateUpdated event for downstream cognitive session / agents
        if self.event_bus:
            twin_updated_event = TwinStateUpdated(
                entity_id=updated_twin.entity_id,
                tenant_id=updated_twin.tenant_id,
                version=updated_twin.version,
                changes=updates,
                correlation_id=event.correlation_id,
            )
            try:
                self.event_bus.publish(twin_updated_event)
                logger.info("Published TwinStateUpdated event", entity_id=str(updated_twin.entity_id))
            except Exception as e:
                logger.error("Failed to publish TwinStateUpdated event", error=str(e))
