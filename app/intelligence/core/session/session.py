"""CognitiveSession — the first-class domain aggregate for Wave-1 autonomous execution.

A CognitiveSession is the single source of truth for one complete autonomous
execution cycle. It encapsulates:

  - Identity (session_id, twin_id)
  - Goals driving the session
  - Context and memory snapshots taken at session start
  - Full execution history (one CycleRecord per loop iteration)
  - Active CognitiveTrace references
  - Budget, permissions, reasoning mode
  - Lifecycle state machine (CREATED → RUNNING → … → COMPLETED/FAILED)

Backward-compat guarantee
--------------------------
All Wave-0 attributes (session_id, mode, metrics, budget, termination_policy,
convergence_state, active_hypotheses, active_assumptions, blackboard_ref,
world_model_snapshot, reasoning_graph_ref) are preserved unchanged so that
the existing CognitivePipeline and ExecutiveIntelligenceOrchestrator keep working
without modification.

Design
------
- CognitiveSession is a DDD Aggregate Root.
- WorkingMemorySnapshot and CycleRecord are immutable Value Objects.
- transition() enforces the lifecycle state machine.
- record_cycle() appends a CycleRecord and updates metrics atomically.
- No infrastructure dependencies — pure domain logic only.
"""

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

import structlog

from app.intelligence.core.session.models import (
    CognitiveMetrics,
    CycleRecord,
    ReasoningMode,
    SessionBudget,
    SessionLifecycleState,
    TerminationPolicy,
    WorkingMemorySnapshot,
)
from app.runtime.agents.permissions import AgentPermission

logger = structlog.get_logger(__name__)


class ConvergenceStatus(StrEnum):
    """Wave-0 convergence status — preserved unchanged."""

    CONVERGED = "CONVERGED"
    CONTINUE_REASONING = "CONTINUE_REASONING"
    REQUEST_MORE_INFORMATION = "REQUEST_MORE_INFORMATION"
    REQUIRE_HUMAN_INPUT = "REQUIRE_HUMAN_INPUT"


class InvalidSessionTransitionError(Exception):
    """Raised when an invalid lifecycle state transition is attempted."""

    def __init__(self, from_state: SessionLifecycleState, to_state: SessionLifecycleState) -> None:
        super().__init__(
            f"Invalid session transition: {from_state} → {to_state}. "
            f"Allowed from {from_state}: {SessionLifecycleState.allowed_transitions().get(from_state, set())}"
        )
        self.from_state = from_state
        self.to_state = to_state


class CognitiveSession:
    """First-class domain aggregate for autonomous cognitive execution.

    Lifecycle
    ---------
        factory creates  →  CREATED
        controller.start →  RUNNING
        external event   →  SUSPENDED  →  RUNNING (resumed)
        loop converges   →  COMPLETED
        unrecoverable    →  FAILED

    Thread-safety
    -------------
    This class is NOT thread-safe. Each session must be owned by a single
    asyncio task. The SessionManager coordinates concurrent sessions.
    """

    def __init__(
        self,
        *,
        twin_id: UUID | None = None,
        goals: list[Any] | None = None,
        context_snapshot_id: UUID | None = None,
        memory_snapshot: WorkingMemorySnapshot | None = None,
        permissions: set[AgentPermission] | None = None,
        mode: ReasoningMode = ReasoningMode.ANALYTICAL,
        budget: SessionBudget | None = None,
        termination_policy: TerminationPolicy | None = None,
    ) -> None:
        # ── Identity ──────────────────────────────────────────────────────────
        self.session_id: str = str(uuid.uuid4())
        self.twin_id: UUID | None = twin_id
        self.created_at: datetime = datetime.now(UTC)

        # ── Lifecycle ─────────────────────────────────────────────────────────
        self._lifecycle_state: SessionLifecycleState = SessionLifecycleState.CREATED
        self._state_transitions: list[tuple[SessionLifecycleState, datetime]] = [
            (SessionLifecycleState.CREATED, self.created_at)
        ]

        # ── Goals & Context ───────────────────────────────────────────────────
        self.goals: list[Any] = goals or []
        self.context_snapshot_id: UUID | None = context_snapshot_id
        self.memory_snapshot: WorkingMemorySnapshot = memory_snapshot or WorkingMemorySnapshot.empty()

        # ── Permissions ───────────────────────────────────────────────────────
        self.permissions: set[AgentPermission] = permissions or set()

        # ── Configuration ─────────────────────────────────────────────────────
        self.mode: ReasoningMode = mode
        self.budget: SessionBudget = budget or SessionBudget()
        self.termination_policy: TerminationPolicy = termination_policy or TerminationPolicy()

        # ── Observability ─────────────────────────────────────────────────────
        self.metrics: CognitiveMetrics = CognitiveMetrics()

        # ── Execution History (Wave-1) ─────────────────────────────────────────
        self.execution_history: list[CycleRecord] = []
        self.active_traces: list[UUID] = []

        # ── Wave-0 backward-compat attributes ────────────────────────────────
        self.convergence_state: ConvergenceStatus = ConvergenceStatus.CONTINUE_REASONING
        self.active_hypotheses: list[Any] = []
        self.active_assumptions: list[Any] = []
        self.blackboard_ref: Any = None
        self.world_model_snapshot: Any = None
        self.reasoning_graph_ref: Any = None

        logger.debug(
            "CognitiveSession created",
            session_id=self.session_id,
            twin_id=str(twin_id) if twin_id else "none",
            mode=mode.value,
        )

    # ── Lifecycle state machine ───────────────────────────────────────────────

    @property
    def lifecycle_state(self) -> SessionLifecycleState:
        return self._lifecycle_state

    @property
    def is_terminal(self) -> bool:
        return self._lifecycle_state in {
            SessionLifecycleState.COMPLETED,
            SessionLifecycleState.FAILED,
        }

    @property
    def is_runnable(self) -> bool:
        return self._lifecycle_state in {
            SessionLifecycleState.RUNNING,
            SessionLifecycleState.CREATED,
        }

    def transition(self, to_state: SessionLifecycleState, reason: str = "") -> None:
        """Transition lifecycle state. Raises InvalidSessionTransitionError on invalid moves."""
        allowed = SessionLifecycleState.allowed_transitions().get(self._lifecycle_state, set())
        if to_state not in allowed:
            raise InvalidSessionTransitionError(self._lifecycle_state, to_state)

        from_state = self._lifecycle_state
        self._lifecycle_state = to_state
        self._state_transitions.append((to_state, datetime.now(UTC)))

        logger.info(
            "Session lifecycle transition",
            session_id=self.session_id,
            from_state=from_state.value,
            to_state=to_state.value,
            reason=reason,
        )

    # ── Execution history ─────────────────────────────────────────────────────

    def record_cycle(self, record: CycleRecord) -> None:
        """Append a completed CycleRecord to the execution history and update metrics."""
        self.execution_history.append(record)
        self.metrics.iteration_count += 1

        if record.duration_ms > 0:
            self.metrics.convergence_duration_ms = int(record.duration_ms)

        logger.debug(
            "Cycle recorded",
            session_id=self.session_id,
            cycle_index=record.cycle_index,
            succeeded=record.succeeded,
            duration_ms=record.duration_ms,
        )

    def register_trace(self, trace_id: UUID) -> None:
        """Register a CognitiveTrace ID as produced during this session."""
        self.active_traces.append(trace_id)

    def add_goal(self, goal: Any) -> None:
        """Add a goal to the active goals list. Goals are not immutable."""
        self.goals.append(goal)

    # ── Budget & termination helpers ──────────────────────────────────────────

    def is_budget_exhausted(self) -> bool:
        """Return True if any budget constraint is exceeded."""
        return self.metrics.iteration_count >= self.budget.max_iterations

    def should_terminate(self) -> bool:
        """Return True if the session should stop looping."""
        return self.is_terminal or self.is_budget_exhausted()

    # ── Wave-0 backward-compat method ────────────────────────────────────────

    def increment_iteration(self) -> None:
        """Wave-0 compatibility: increment iteration counter."""
        self.metrics.iteration_count += 1

    # ── Repr ──────────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return (
            f"CognitiveSession("
            f"id={self.session_id[:8]}…, "
            f"twin={str(self.twin_id)[:8] if self.twin_id else 'none'}…, "
            f"state={self._lifecycle_state.value}, "
            f"cycles={len(self.execution_history)}, "
            f"goals={len(self.goals)}"
            f")"
        )
