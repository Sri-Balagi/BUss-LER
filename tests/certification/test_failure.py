import pytest
from app.intelligence.integration.orchestrator import ExecutiveIntelligenceOrchestrator
from app.intelligence.integration.errors import IntelligenceError
from app.intelligence.runtime_bridge.bridge import IntelligenceRuntimeBridge
from app.intelligence.decision.planning.models import ExecutiveDirective
from app.intelligence.runtime_bridge.errors import RuntimeIntegrationError

def test_intelligence_failure_recovery(monkeypatch):
    orchestrator = ExecutiveIntelligenceOrchestrator()
    
    # Inject failure into Observation layer
    def mock_analyze(*args, **kwargs):
        raise Exception("Agent registry failed to load capability")
        
    monkeypatch.setattr(orchestrator.pipeline.situation_engine, "analyze", mock_analyze)
    
    with pytest.raises(IntelligenceError) as exc:
        orchestrator.process_request("Process this")
        
    assert "Agent registry failed" in str(exc.value)
    # The pipeline catches the generic exception and wraps it safely
    
def test_runtime_failure_propagation(monkeypatch):
    bridge = IntelligenceRuntimeBridge()
    
    # Inject failure into Supervisor Adapter
    def mock_dispatch(*args, **kwargs):
        raise RuntimeIntegrationError("Scheduler queue full", "SupervisorAdapter")
        
    monkeypatch.setattr(bridge.adapter, "dispatch_directive", mock_dispatch)
    
    directive = ExecutiveDirective(directive_id="d1", intent="Fail", success_conditions=[])
    
    with pytest.raises(RuntimeIntegrationError) as exc:
        bridge.execute_directives([directive])
        
    assert "Scheduler queue full" in str(exc.value)
    assert exc.value.component == "SupervisorAdapter"
