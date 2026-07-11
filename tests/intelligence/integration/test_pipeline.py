import pytest

from app.intelligence.integration.errors import IntelligenceError
from app.intelligence.integration.models import CognitivePipelineState
from app.intelligence.integration.orchestrator import ExecutiveIntelligenceOrchestrator


def test_pipeline_success():
    from app.bootstrap.container import build_container, get_container
    from app.bootstrap.container import _global_container
    container = get_container() if _global_container else build_container()
    orchestrator = container.resolve(ExecutiveIntelligenceOrchestrator)
    result = orchestrator.process_request("Maximize profits")

    assert result.summary.state == CognitivePipelineState.COMPLETED
    assert result.intent is not None
    assert result.situation is not None
    assert len(result.objectives) > 0
    assert result.decision is not None
    assert result.plan is not None
    assert result.reflection is not None
    assert result.summary.metrics.duration_ms >= 0
    assert result.summary.metrics.artifacts_produced > 0


def test_pipeline_error_propagation(monkeypatch):
    from app.bootstrap.container import build_container, get_container
    from app.bootstrap.container import _global_container
    container = get_container() if _global_container else build_container()
    orchestrator = container.resolve(ExecutiveIntelligenceOrchestrator)

    # Mock an error in the strategy layer
    def mock_formulate(*args, **kwargs):
        raise IntelligenceError("Forced failure", "Strategy")

    monkeypatch.setattr(
        orchestrator.pipeline.objective_engine, "create_objective_from_intent", mock_formulate
    )

    with pytest.raises(IntelligenceError) as excinfo:
        orchestrator.process_request("Fail now")

    assert "Forced failure" in str(excinfo.value)
    assert excinfo.value.layer == "Strategy"
