"""Wave-0 + Wave-1 session domain models.

Wave-0 classes (ReasoningMode, CognitiveMetrics, SessionBudget, TerminationPolicy)
are untouched. Wave-1 adds SessionLifecycleState, WorkingMemorySnapshot, and
CycleRecord as first-class domain value objects.
"""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

# ── Wave-0 models (unchanged) ─────────────────────────────────────────────────

class ReasoningMode(StrEnum):
    """Declarative reasoning modes that affect controller behavior."""

    FAST = "FAST"
    ANALYTICAL = "ANALYTICAL"
    EXPLORATORY = "EXPLORATORY"
    CONSERVATIVE = "CONSERVATIVE"
    EMERGENCY = "EMERGENCY"
    CREATIVE = "CREATIVE"


class CognitiveMetrics(BaseModel):
    """Passive observability metrics for a cognitive session."""

    iteration_count: int = 0
    convergence_duration_ms: int = 0
    planning_latency_ms: int = 0
    discarded_hypotheses: int = 0
    branching_factor: float = 0.0
    confidence_progression: list[float] = Field(default_factory=list)
    uncertainty_progression: list[float] = Field(default_factory=list)
    simulation_count: int = 0


class SessionBudget(BaseModel):
    """Budget constraints for a cognitive session."""

    max_iterations: int = 10
    max_duration_ms: int = 60000
    max_llm_tokens: int | None = None
    max_simulations: int = 5


class TerminationPolicy(BaseModel):
    """Rules defining when a cognitive loop should break."""

    target_confidence: float = 0.85
    max_uncertainty: float = 0.3
    require_stable_assumptions: bool = True
    enforce_strict_budget: bool = True


# ── Wave-1 value objects ──────────────────────────────────────────────────────

class SessionLifecycleState(StrEnum):
    """Lifecycle states of a CognitiveSession.

    State machine:
        CREATED → RUNNING → SUSPENDED → RUNNING (resume)
                          → COMPLETED
                          → FAILED
    """

    CREATED = "CREATED"
    RUNNING = "RUNNING"
    SUSPENDED = "SUSPENDED"
    AWAITING_INPUT = "AWAITING_INPUT"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

    # Valid transitions map — enforced by CognitiveSession.transition()
    @classmethod
    def allowed_transitions(cls) -> dict["SessionLifecycleState", set["SessionLifecycleState"]]:
        return {
            cls.CREATED: {cls.RUNNING, cls.FAILED},
            cls.RUNNING: {cls.SUSPENDED, cls.AWAITING_INPUT, cls.COMPLETED, cls.FAILED},
            cls.SUSPENDED: {cls.RUNNING, cls.FAILED},
            cls.AWAITING_INPUT: {cls.RUNNING, cls.FAILED},
            cls.COMPLETED: set(),
            cls.FAILED: set(),
        }


class WorkingMemorySnapshot(BaseModel):
    """Immutable snapshot of a twin's working memory at session start.

    Value Object — created once, never mutated.
    """

    captured_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    entries: dict[str, Any] = Field(default_factory=dict)
    entry_count: int = 0

    @classmethod
    def empty(cls) -> "WorkingMemorySnapshot":
        return cls(entries={}, entry_count=0)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WorkingMemorySnapshot":
        return cls(entries=dict(data), entry_count=len(data))


class CycleRecord(BaseModel):
    """Immutable record of a single completed cognitive loop iteration.

    Value Object — appended to CognitiveSession.execution_history after each loop.
    """

    cycle_index: int
    cycle_id: UUID = Field(default_factory=uuid4)
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    duration_ms: float = 0.0

    # Phase outcomes
    phase_results: dict[str, str] = Field(
        default_factory=dict,
        description="Map of phase_name → outcome (COMPLETED | SKIPPED | FAILED).",
    )
    artifacts_produced: int = 0

    # Outcome
    succeeded: bool = True
    failure_reason: str | None = None

    # References to key artifacts for traceability
    intent_summary: str | None = None
    decision_summary: str | None = None
    plan_step_count: int = 0
    agent_result_summary: str | None = None
    heuristics_extracted: int = 0
