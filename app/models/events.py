import uuid
from typing import Optional
from datetime import datetime, timezone
from enum import Enum
from pydantic import Field
from app.models.schemas import DomainBaseModel


class EventType(str, Enum):
    """Lifecycle event types."""
    CREATED = "CREATED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class DomainEvent(DomainBaseModel):
    """Base class for all BizOS events."""
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str = Field(..., description="Trace ID linking operations together.")
    causation_id: Optional[str] = Field(default=None, description="The ID of the event that caused this event.")
    source: str = Field(default="bizos-core", description="The system that emitted the event.")
    version: str = Field(default="1.0", description="Event schema version.")


class MemoryLifecycleEvent(DomainEvent):
    """Event triggered during memory lifecycle transitions."""
    memory_id: uuid.UUID = Field(...)
    twin_id: uuid.UUID = Field(...)
    event_type: EventType = Field(...)
