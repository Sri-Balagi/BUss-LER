import uuid
from app.intelligence.decision.planning.models import ExecutiveDirective
from app.intelligence.runtime_bridge.interfaces import ISupervisorAdapter
from app.intelligence.runtime_bridge.models import ExecutionSummary, RuntimeExecutionStatus, RuntimeMetrics
from app.intelligence.runtime_bridge.errors import RuntimeIntegrationError

class SupervisorAdapter(ISupervisorAdapter):
    """
    Translates ExecutiveDirectives into Supervisor requests.
    Mocks integration with the frozen M5 Runtime Supervisor.
    """
    def dispatch_directive(self, directive: ExecutiveDirective) -> str:
        # Translate to Supervisor request
        # Mocking Supervisor creation of TaskDAG and return of a handle
        if not directive.intent:
            raise RuntimeIntegrationError("Directive lacks intent.", "SupervisorAdapter")
            
        return f"handle_{uuid.uuid4()}"
        
    def get_execution_summary(self, handle: str) -> ExecutionSummary:
        # Mocking collection of ExecutionSummary from the Supervisor/Runtime
        if not handle.startswith("handle_"):
            raise RuntimeIntegrationError("Invalid execution handle.", "SupervisorAdapter")
            
        return ExecutionSummary(
            summary_id=str(uuid.uuid4()),
            overall_status=RuntimeExecutionStatus.COMPLETED,
            directive_mappings=[],
            metrics=RuntimeMetrics(execution_time_ms=120.0, tasks_spawned=3, capabilities_invoked=1)
        )
