import enum
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class TwinLifecycleStatus(enum.StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"
    SYNCHRONIZING = "SYNCHRONIZING"


class TwinSnapshot(BaseModel):
    """Immutable capture of a twin's state at a point in time."""
    snapshot_id: UUID = Field(default_factory=uuid4)
    entity_id: UUID
    entity_type: str
    captured_at: datetime = Field(default_factory=datetime.utcnow)
    state: dict[str, Any]

    class Config:
        frozen = True


class DigitalTwinState(BaseModel):
    """The mutable active representation of a business entity."""
    entity_id: UUID
    tenant_id: UUID
    entity_type: str
    status: TwinLifecycleStatus = Field(default=TwinLifecycleStatus.ACTIVE)
    last_synced_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = Field(default=1)

    # The actual aggregated business data from BKG and Memory
    properties: dict[str, Any] = Field(default_factory=dict)

    # References to related entities (graph edges projected into the twin)
    related_entities: list[UUID] = Field(default_factory=list)
