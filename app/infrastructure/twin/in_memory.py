import threading
from uuid import UUID

from app.domain.intelligence.capability import CapabilityMetadata, CapabilityType
from app.domain.intelligence.provider import ProviderLifecycleStatus
from app.domain.twin.models import DigitalTwinState, TwinSnapshot
from app.domain.twin.provider import ITwinProvider


class InMemoryTwinProvider(ITwinProvider):
    """Configurable In-Memory provider for the Digital Twin."""

    def __init__(self):
        self._twins: dict[UUID, DigitalTwinState] = {}
        self._snapshots: dict[UUID, TwinSnapshot] = {}
        self._lock = threading.Lock()

    def get_metadata(self) -> CapabilityMetadata:
        return CapabilityMetadata(
            capability_id="twin-in-memory",
            provider_name="InMemoryTwinProvider",
            provider_version="1.0",
            capability_type=CapabilityType.TWIN,
            priority=1,
            supported_features=["real-time", "snapshots"]
        )

    def get_status(self) -> ProviderLifecycleStatus:
        return ProviderLifecycleStatus.READY

    async def get_twin(self, tenant_id: UUID, entity_id: UUID) -> DigitalTwinState | None:
        with self._lock:
            twin = self._twins.get(entity_id)
            if twin and twin.tenant_id == tenant_id:
                return twin
            return None

    async def save_twin(self, twin: DigitalTwinState) -> None:
        with self._lock:
            self._twins[twin.entity_id] = twin

    async def get_snapshot(self, snapshot_id: UUID) -> TwinSnapshot | None:
        with self._lock:
            return self._snapshots.get(snapshot_id)

    async def save_snapshot(self, snapshot: TwinSnapshot) -> None:
        with self._lock:
            self._snapshots[snapshot.snapshot_id] = snapshot
