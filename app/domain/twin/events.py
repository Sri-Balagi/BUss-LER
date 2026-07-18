from typing import Any, Dict
from uuid import UUID

from app.shared.events.models import DomainEvent
from app.domain.twin.models import TwinLifecycleStatus


class TwinCreated(DomainEvent):
    entity_id: UUID
    tenant_id: UUID
    entity_type: str


class TwinStateUpdated(DomainEvent):
    entity_id: UUID
    tenant_id: UUID
    version: int
    changes: Dict[str, Any]


class TwinDesynchronized(DomainEvent):
    entity_id: UUID
    tenant_id: UUID
    reason: str
    status: TwinLifecycleStatus
