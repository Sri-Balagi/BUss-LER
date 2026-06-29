import pytest
from app.intelligence.runtime_bridge.bridge import IntelligenceRuntimeBridge
from app.intelligence.decision.planning.models import ExecutiveDirective
from app.intelligence.runtime_bridge.models import RuntimeExecutionStatus
from app.intelligence.runtime_bridge.errors import RuntimeIntegrationError

def test_bridge_execute_directives():
    bridge = IntelligenceRuntimeBridge()
    d1 = ExecutiveDirective(directive_id="d1", intent="Test intent", success_conditions=[])
    
    result = bridge.execute_directives([d1])
    
    assert result.summary.overall_status == RuntimeExecutionStatus.COMPLETED
    assert len(result.summary.directive_mappings) == 1
    assert result.summary.directive_mappings[0].directive_id == "d1"
    assert result.summary.directive_mappings[0].status == RuntimeExecutionStatus.COMPLETED
    assert result.summary.metrics.tasks_spawned == 3
    assert result.summary.metrics.capabilities_invoked == 1
    assert result.summary.metrics.execution_time_ms == 120.0

def test_bridge_no_directives():
    bridge = IntelligenceRuntimeBridge()
    result = bridge.execute_directives([])
    
    assert result.summary.overall_status == RuntimeExecutionStatus.COMPLETED
    assert len(result.summary.directive_mappings) == 0

def test_bridge_error_propagation():
    bridge = IntelligenceRuntimeBridge()
    d2 = ExecutiveDirective(directive_id="d2", intent="", success_conditions=[])
    
    with pytest.raises(RuntimeIntegrationError) as excinfo:
        bridge.execute_directives([d2])
        
    assert "Directive lacks intent" in str(excinfo.value)
    assert excinfo.value.component == "SupervisorAdapter"
