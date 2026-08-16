from datetime import datetime
from uuid import UUID

from app.domain.intelligence.capability import CapabilityType
from app.domain.intelligence.context import IntelligenceContext
from app.domain.intelligence.provider import ICapabilityRegistry
from app.domain.twin.models import DigitalTwinState
from app.domain.twin.provider import ITwinProvider


class DigitalTwinService:
    """Primary orchestrator for the Twin lifecycle."""

    def __init__(self, capability_registry: ICapabilityRegistry):
        self._registry = capability_registry

    def _get_provider(self) -> ITwinProvider:
        provider = self._registry.resolve_provider(CapabilityType.TWIN)
        if not provider:
            raise RuntimeError("No active ITwinProvider found in Capability Registry.")
        return provider # type: ignore

    async def get_twin(self, context: IntelligenceContext, entity_id: UUID) -> DigitalTwinState | None:
        provider = self._get_provider()
        return await provider.get_twin(context.tenant_id, entity_id) # type: ignore

    async def create_twin(self, context: IntelligenceContext, entity_id: UUID, entity_type: str) -> DigitalTwinState:
        provider = self._get_provider()
        twin = DigitalTwinState(
            entity_id=entity_id,
            tenant_id=context.tenant_id, # type: ignore
            entity_type=entity_type
        )
        await provider.save_twin(twin)
        return twin

    async def update_twin_properties(self, context: IntelligenceContext, entity_id: UUID, properties: dict) -> DigitalTwinState | None:
        provider = self._get_provider()
        twin = await provider.get_twin(context.tenant_id, entity_id) # type: ignore
        if not twin:
            return None

        twin.properties.update(properties)
        twin.version += 1
        twin.last_synced_at = datetime.utcnow()
        await provider.save_twin(twin)
        return twin
