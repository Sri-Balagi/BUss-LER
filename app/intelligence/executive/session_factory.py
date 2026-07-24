"""Factory for creating rich CognitiveSession aggregates.

The SessionFactory bridges the gap between raw intents (Wave-0 Intake)
and the autonomous execution environment (Wave-1 CognitiveSession).
"""

from uuid import UUID

from app.application.twin.get_twin import GetTwinUseCase
from app.intelligence.core.session.models import (
    ReasoningMode,
    SessionBudget,
    TerminationPolicy,
    WorkingMemorySnapshot,
)
from app.intelligence.core.session.session import CognitiveSession
from app.runtime.agents.permissions import AgentPermission


class SessionFactory:
    """Assembles a valid CognitiveSession from external state and requests."""

    def __init__(self, get_twin_use_case: GetTwinUseCase) -> None:
        self.get_twin_use_case = get_twin_use_case

    async def create_session(
        self,
        twin_id: UUID | None,
        raw_request: str | None = None,
        mode: ReasoningMode = ReasoningMode.ANALYTICAL,
    ) -> CognitiveSession:
        """Create a new CognitiveSession, optionally snapping twin memory state."""

        # If twin_id provided, we would normally snapshot memory here.
        # For Milestone 7, we initialize an empty snapshot to respect the contract
        # without introducing heavy memory engine coupling prematurely.
        memory_snapshot = WorkingMemorySnapshot.empty()

        # Define baseline autonomous permissions.
        # These will be dynamically shaped by the ContextEngine in M8.
        baseline_permissions = {
            AgentPermission.READ_MEMORY,
            AgentPermission.WRITE_MEMORY,
            AgentPermission.MODIFY_GOALS,
        }

        # Setup budget based on mode.
        budget = self._default_budget_for_mode(mode)
        termination_policy = self._default_termination_for_mode(mode)

        session = CognitiveSession(
            twin_id=twin_id,
            memory_snapshot=memory_snapshot,
            permissions=baseline_permissions,
            mode=mode,
            budget=budget,
            termination_policy=termination_policy,
        )

        # Attach raw request as a mock active goal to kickstart the loop.
        if raw_request:
            session.add_goal({"source": "user_request", "raw": raw_request})

        return session

    def _default_budget_for_mode(self, mode: ReasoningMode) -> SessionBudget:
        if mode == ReasoningMode.FAST:
            return SessionBudget(max_iterations=3, max_duration_ms=10000)
        elif mode == ReasoningMode.EXPLORATORY:
            return SessionBudget(max_iterations=20, max_duration_ms=120000)
        return SessionBudget(max_iterations=10, max_duration_ms=60000)

    def _default_termination_for_mode(self, mode: ReasoningMode) -> TerminationPolicy:
        if mode == ReasoningMode.FAST:
            return TerminationPolicy(target_confidence=0.7, max_uncertainty=0.5)
        elif mode == ReasoningMode.CONSERVATIVE:
            return TerminationPolicy(target_confidence=0.95, max_uncertainty=0.1)
        return TerminationPolicy()
