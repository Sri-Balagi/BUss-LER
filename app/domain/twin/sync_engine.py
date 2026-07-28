"""Digital Twin Synchronization Engine.

Synchronizes agent execution outcomes, operational changes, and business metrics
directly into the active DigitalTwinState.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from app.domain.twin.models import DigitalTwinState, TwinLifecycleStatus, TwinSnapshot


class DigitalTwinSyncEngine:
    """Manages active Digital Twin state updates and snapshot history."""

    def __init__(self, tenant_id: UUID, entity_id: UUID, entity_type: str = "LOCATION"):
        self.active_twin = DigitalTwinState(
            entity_id=entity_id,
            tenant_id=tenant_id,
            entity_type=entity_type,
            status=TwinLifecycleStatus.ACTIVE,
            properties={
                "location_name": "Bella Vista Downtown",
                "tables_count": 40,
                "tables_occupied": 34,
                "head_chef": "Marco Rossi (Sick)",
                "active_lead_chef": "Sofia (Promoted Sous Chef)",
                "staff_shortage": 2,
                "wait_time_min": 47,
                "wait_time_sla_min": 20,
                "orders_queued": 23,
                "vip_arrival": "Apex Corp (18 guests at 20:00)",
                "vip_reserved_tables": "Tables 15-22",
                "vip_server": "Carlos",
                "kpi_guest_sat": "2.1 stars -> 4.3 target",
            },
        )
        self.snapshots: list[TwinSnapshot] = []

    def update_property(self, key: str, value: Any) -> None:
        """Update a twin property and increment twin version."""
        self.active_twin.properties[key] = value
        self.active_twin.version += 1
        self.active_twin.last_synced_at = datetime.utcnow()
        self._capture_snapshot()

    def batch_update_properties(self, updates: Dict[str, Any]) -> None:
        """Apply a batch of property updates."""
        for k, v in updates.items():
            self.active_twin.properties[k] = v
        self.active_twin.version += 1
        self.active_twin.last_synced_at = datetime.utcnow()
        self._capture_snapshot()

    def get_state(self) -> DigitalTwinState:
        return self.active_twin

    def _capture_snapshot(self) -> TwinSnapshot:
        snapshot = TwinSnapshot(
            snapshot_id=uuid4(),
            entity_id=self.active_twin.entity_id,
            entity_type=self.active_twin.entity_type,
            captured_at=datetime.utcnow(),
            state=dict(self.active_twin.properties),
        )
        self.snapshots.append(snapshot)
        return snapshot
