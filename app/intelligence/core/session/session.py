import uuid
from enum import Enum
from typing import Any, Optional

from app.intelligence.core.session.models import (
    CognitiveMetrics,
    ReasoningMode,
    SessionBudget,
    TerminationPolicy,
)


class ConvergenceStatus(str, Enum):
    CONVERGED = "CONVERGED"
    CONTINUE_REASONING = "CONTINUE_REASONING"
    REQUEST_MORE_INFORMATION = "REQUEST_MORE_INFORMATION"
    REQUIRE_HUMAN_INPUT = "REQUIRE_HUMAN_INPUT"

class CognitiveSession:
    """
    The complete execution context for the Intelligence Layer.
    Isolated entirely from the M5 Runtime ExecutionSession.
    """
    def __init__(
        self,
        mode: ReasoningMode = ReasoningMode.ANALYTICAL,
        budget: SessionBudget | None = None,
        termination_policy: TerminationPolicy | None = None
    ):
        self.session_id: str = str(uuid.uuid4())
        self.mode: ReasoningMode = mode
        self.metrics: CognitiveMetrics = CognitiveMetrics()
        self.budget: SessionBudget = budget or SessionBudget()
        self.termination_policy: TerminationPolicy = termination_policy or TerminationPolicy()

        self.convergence_state: ConvergenceStatus = ConvergenceStatus.CONTINUE_REASONING
        self.active_hypotheses: list[Any] = []
        self.active_assumptions: list[Any] = []

        # In a real implementation these would be typed references
        self.blackboard_ref: Any = None
        self.world_model_snapshot: Any = None
        self.reasoning_graph_ref: Any = None

    def increment_iteration(self):
        self.metrics.iteration_count += 1
