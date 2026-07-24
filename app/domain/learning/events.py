from uuid import UUID

from app.domain.learning.models import LearningResult
from app.shared.events.models import DomainEvent


class LearningStarted(DomainEvent):
    """Event emitted when the learning pipeline begins processing a request."""
    agent_id: UUID
    tenant_id: UUID | None
    iteration: int


class KnowledgeExtracted(DomainEvent):
    """Event emitted when knowledge is extracted from reflection feedback."""
    agent_id: UUID
    tenant_id: UUID | None
    extracted_items_count: int


class KnowledgeConsolidated(DomainEvent):
    """Event emitted when knowledge has been successfully persisted to memory/BKG/vector store."""
    agent_id: UUID
    tenant_id: UUID | None
    consolidated_items_count: int


class LearningCompleted(DomainEvent):
    """Event emitted when the learning pipeline successfully completes."""
    agent_id: UUID
    tenant_id: UUID | None
    iteration: int
    result: LearningResult


class LearningFailed(DomainEvent):
    """Event emitted when the learning pipeline fails."""
    agent_id: UUID
    tenant_id: UUID | None
    iteration: int
    error: str
