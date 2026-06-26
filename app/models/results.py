"""BizOS result models — outputs from service operations.

Results follow the CQRS pattern: services return typed Result objects
rather than raw domain models or dicts, enabling richer metadata (event counts,
trace IDs, etc.) without polluting domain models.
"""

from typing import List, Optional
from uuid import UUID
from pydantic import Field

from app.models.schemas import DomainBaseModel
from app.models.memory import Memory
from app.models.intent import Intent, IntentAnalysis
from app.models.goal import Goal, GoalIntentLink
from app.models.plan import Plan
from app.models.recommendation import Recommendation
from app.models.cognitive_trace import CognitiveTrace


# =============================================================================
# Memory Results (Milestone 2)
# =============================================================================


class CreateMemoryResult(DomainBaseModel):
    """Result of a memory creation operation."""
    memory: Memory
    dispatched_events: int = Field(default=0, description="Number of background events dispatched.")


class MemorySearchResultItem(DomainBaseModel):
    """A single matched memory with its similarity score."""
    memory: Memory
    similarity_score: float


class SearchMemoryResult(DomainBaseModel):
    """Result of a semantic search operation."""
    items: List[MemorySearchResultItem]
    total_count: int


class DeleteMemoryResult(DomainBaseModel):
    """Result of a memory deletion."""
    success: bool
    memory_id: str


# =============================================================================
# Intent Results (Milestone 3)
# =============================================================================


class CreateIntentResult(DomainBaseModel):
    """Result of an intent creation operation."""
    intent: Intent
    dispatched_events: int = Field(default=0)


class ClassifyIntentResult(DomainBaseModel):
    """Result of an intent classification operation.

    Contains the validated IntentAnalysis and the updated Intent entity.
    The cognitive_trace is populated when tracing is enabled.
    """
    intent: Intent
    analysis: IntentAnalysis
    cognitive_trace: Optional[CognitiveTrace] = None
    dispatched_events: int = Field(default=0)


# =============================================================================
# Goal Results (Milestone 3)
# =============================================================================


class CreateGoalResult(DomainBaseModel):
    """Result of a goal creation operation."""
    goal: Goal
    dispatched_events: int = Field(default=0)


class LinkIntentToGoalResult(DomainBaseModel):
    """Result of linking an intent to a goal."""
    link: GoalIntentLink


# =============================================================================
# Plan Results (Milestone 3)
# =============================================================================


class GeneratePlanResult(DomainBaseModel):
    """Result of a plan generation operation."""
    plan: Plan
    cognitive_trace: Optional[CognitiveTrace] = None
    dispatched_events: int = Field(default=0)


# =============================================================================
# Recommendation Results (Milestone 3)
# =============================================================================


class GenerateRecommendationsResult(DomainBaseModel):
    """Result of a recommendation generation operation."""
    recommendations: List[Recommendation]
    cognitive_trace: Optional[CognitiveTrace] = None
    dispatched_events: int = Field(default=0)


# =============================================================================
# Cognitive Trace Results (Milestone 3)
# =============================================================================


class CreateCognitiveTraceResult(DomainBaseModel):
    """Result of creating a cognitive trace record."""
    trace: CognitiveTrace
    dispatched_events: int = Field(default=0)
