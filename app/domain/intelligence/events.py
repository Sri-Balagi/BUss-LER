from typing import Optional
from uuid import UUID

from app.shared.events.models import DomainEvent
from app.domain.intelligence.platform import UnifiedExecutionResult


class UnifiedExecutionStarted(DomainEvent):
    """Event emitted when a unified execution request begins."""
    tenant_id: Optional[UUID] = None
    agent_id: Optional[UUID] = None
    request_type: str


class CapabilityExecutionStarted(DomainEvent):
    """Event emitted when a specific capability begins execution within the unified platform."""
    tenant_id: Optional[UUID] = None
    agent_id: Optional[UUID] = None
    capability_type: str


class CapabilityExecutionCompleted(DomainEvent):
    """Event emitted when a specific capability successfully completes execution."""
    tenant_id: Optional[UUID] = None
    agent_id: Optional[UUID] = None
    capability_type: str
    latency_ms: float


class UnifiedExecutionCompleted(DomainEvent):
    """Event emitted when a unified execution request successfully completes."""
    tenant_id: Optional[UUID] = None
    agent_id: Optional[UUID] = None
    request_type: str
    result: UnifiedExecutionResult


class UnifiedExecutionFailed(DomainEvent):
    """Event emitted when a unified execution request fails."""
    tenant_id: Optional[UUID] = None
    agent_id: Optional[UUID] = None
    request_type: str
    error: str
