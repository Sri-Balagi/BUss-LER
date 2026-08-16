"""CognitiveContext model for the Intent Context Builder.

CognitiveContext is the assembled context window produced by the ContextBuilder.
It is scoped to intent understanding, planning, and recommendation generation.

IMPORTANT: This is NOT the full enterprise Context Engine planned for Milestone 4.
Milestone 4 will introduce a full ContextEngine that extends this foundation.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from app.intelligence.intake.intent.intent import Intent
from app.intelligence.strategy.goals.goal import Goal
from app.interfaces.http.schemas.base import DomainBaseModel


class ContextMemory(DomainBaseModel):
    """A memory retrieved for context."""

    memory_id: UUID
    content: str
    similarity_score: float
    category: str | None = None


class CognitiveContext(DomainBaseModel):
    """Assembled context window for intent-driven cognitive operations.

    Produced by ContextBuilder.build() and passed to:
      - PlanningEngine.generate_plan()
      - RecommendationEngine.generate_recommendations()

    Scoped to Milestone 3. Future milestones extend but do not redesign.
    """

    twin_id: UUID
    assembled_at: datetime

    # --- Current cognitive state ---
    current_intent: Intent | None = Field(
        default=None,
        description="Intent that triggered this context assembly.",
    )

    # --- Active goals (from GoalService) ---
    active_goals: list[Goal] = Field(
        default_factory=list,
        description="Active Goal records for this twin, ordered by priority descending.",
    )

    # --- Relevant memories (from MemoryService semantic search) ---
    relevant_memories: list[ContextMemory] = Field(
        default_factory=list,
        description=(
            "Memory records retrieved via semantic search using the intent's raw_text. "
            "Each entry includes memory content + similarity_score."
        ),
    )

    # --- Conversation placeholder (Milestone 4 will replace this) ---
    recent_conversation: list[dict[str, Any]] = Field(
        default_factory=list,
        description=(
            "Recent conversation turns (placeholder). "
            "Full conversation integration is a Milestone 4 responsibility."
        ),
    )

    # --- Business state snapshot ---
    business_state: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Lightweight business state snapshot derived from the Digital Twin. "
            "Used to ground AI recommendations in current business reality."
        ),
    )

    # --- Trace IDs for observability ---
    memory_ids_used: list[UUID] = Field(
        default_factory=list,
        description="IDs of Memory records included in relevant_memories.",
    )
    goal_ids_used: list[UUID] = Field(
        default_factory=list,
        description="IDs of Goal records included in active_goals.",
    )

    # --- Token budget ---
    estimated_token_count: int = Field(
        default=0,
        ge=0,
        description="Estimated token count of this context window for AI Kernel budget management.",
    )

    metadata: dict[str, Any] = Field(default_factory=dict)
