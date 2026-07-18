from typing import Optional, List
from uuid import UUID

from app.shared.events.models import DomainEvent
from app.domain.learning.models import LearningResult, LearningMetrics


class LearningStarted(DomainEvent):
    """Event emitted when the learning pipeline begins processing a request."""
    agent_id: UUID
    tenant_id: Optional[UUID]
    iteration: int


class KnowledgeExtracted(DomainEvent):
    """Event emitted when knowledge is extracted from reflection feedback."""
    agent_id: UUID
    tenant_id: Optional[UUID]
    extracted_items_count: int


class KnowledgeConsolidated(DomainEvent):
    """Event emitted when knowledge has been successfully persisted to memory/BKG/vector store."""
    agent_id: UUID
    tenant_id: Optional[UUID]
    consolidated_items_count: int


class LearningCompleted(DomainEvent):
    """Event emitted when the learning pipeline successfully completes."""
    agent_id: UUID
    tenant_id: Optional[UUID]
    iteration: int
    result: LearningResult


class LearningFailed(DomainEvent):
    """Event emitted when the learning pipeline fails."""
    agent_id: UUID
    tenant_id: Optional[UUID]
    iteration: int
    error: str
