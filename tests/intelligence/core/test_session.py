import pytest
from app.intelligence.core.session.models import ReasoningMode
from app.intelligence.core.session.session import CognitiveSession, ConvergenceStatus

def test_cognitive_session_initialization():
    session = CognitiveSession(mode=ReasoningMode.FAST)
    assert session.mode == ReasoningMode.FAST
    assert session.convergence_state == ConvergenceStatus.CONTINUE_REASONING
    assert session.metrics.iteration_count == 0
    assert session.budget.max_iterations == 10
    assert session.termination_policy.target_confidence == 0.85

def test_session_increment_iteration():
    session = CognitiveSession()
    assert session.metrics.iteration_count == 0
    session.increment_iteration()
    assert session.metrics.iteration_count == 1
