from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import Field

from app.domain.intelligence.context import IntelligenceContext
from app.domain.intelligence.telemetry import IntelligenceMetrics
from app.domain.cognition.models import ReflectionFeedback


class LearningContext(IntelligenceContext):
    """Context propagated through the learning pipeline."""
    agent_id: UUID
    tenant_id: Optional[UUID] = None
    iteration: int
    feedback: ReflectionFeedback
    
    class Config:
        frozen = True


class LearningMetrics(IntelligenceMetrics):
    """Telemetry data for learning consolidation."""
    extraction_time_ms: float = 0.0
    consolidation_time_ms: float = 0.0
    items_consolidated: int = 0


class LearningResult(IntelligenceContext):
    """Result of a learning consolidation cycle."""
    success: bool
    metrics: LearningMetrics
    consolidated_items: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    
    class Config:
        frozen = True
