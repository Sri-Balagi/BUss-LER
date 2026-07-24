from typing import Any
from uuid import UUID

from app.domain.twin.models import TwinLifecycleStatus
from app.shared.events.models import DomainEvent


class TwinCreated(DomainEvent):
    entity_id: UUID
    tenant_id: UUID
    entity_type: str


class TwinStateUpdated(DomainEvent):
    entity_id: UUID
    tenant_id: UUID
    version: int  # type: ignore[assignment]  # Entity state integer version shadows DomainEvent schema version string.
    changes: dict[str, Any]



class TwinDesynchronized(DomainEvent):
    entity_id: UUID
    tenant_id: UUID
    reason: str
    status: TwinLifecycleStatus
