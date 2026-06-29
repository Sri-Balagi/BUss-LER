import pytest
from app.intelligence.runtime_bridge.supervisor_adapter import SupervisorAdapter
from app.intelligence.decision.planning.models import ExecutiveDirective
from app.intelligence.runtime_bridge.errors import RuntimeIntegrationError
from app.intelligence.runtime_bridge.models import RuntimeExecutionStatus

def test_supervisor_adapter_dispatch():
    adapter = SupervisorAdapter()
    directive = ExecutiveDirective(directive_id="d1", intent="Some intent", success_conditions=[])
    
    handle = adapter.dispatch_directive(directive)
    assert handle.startswith("handle_")

def test_supervisor_adapter_dispatch_error():
    adapter = SupervisorAdapter()
    directive = ExecutiveDirective(directive_id="d2", intent="", success_conditions=[])
    
    with pytest.raises(RuntimeIntegrationError) as excinfo:
        adapter.dispatch_directive(directive)
        
    assert "Directive lacks intent" in str(excinfo.value)

def test_supervisor_adapter_get_summary():
    adapter = SupervisorAdapter()
    
    summary = adapter.get_execution_summary("handle_123")
    assert summary.overall_status == RuntimeExecutionStatus.COMPLETED
    assert summary.metrics.execution_time_ms == 120.0
    
def test_supervisor_adapter_get_summary_error():
    adapter = SupervisorAdapter()
    
    with pytest.raises(RuntimeIntegrationError) as excinfo:
        adapter.get_execution_summary("invalid")
        
    assert "Invalid execution handle" in str(excinfo.value)
