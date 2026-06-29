import uuid
from typing import List
from app.intelligence.decision.planning.models import ExecutiveDirective
from app.intelligence.runtime.interfaces import IIntelligenceRuntimeBridge, ISupervisorAdapter
from app.intelligence.runtime.models import RuntimeIntegrationResult, ExecutionSummary, RuntimeExecutionStatus, DirectiveExecutionMapping, RuntimeMetrics
from app.intelligence.runtime.errors import RuntimeIntegrationError
from app.intelligence.runtime.supervisor_adapter import SupervisorAdapter

class IntelligenceRuntimeBridge(IIntelligenceRuntimeBridge):
    """
    Acts as the exclusive translation boundary between M6 Intelligence and M5 Runtime.
    """
    def __init__(self, adapter: ISupervisorAdapter = None):
        self.adapter = adapter or SupervisorAdapter()
        
    def execute_directives(self, directives: List[ExecutiveDirective]) -> RuntimeIntegrationResult:
        if not directives:
            return RuntimeIntegrationResult(
                result_id=str(uuid.uuid4()),
                summary=ExecutionSummary(
                    summary_id=str(uuid.uuid4()),
                    overall_status=RuntimeExecutionStatus.COMPLETED,
                    directive_mappings=[],
                    metrics=RuntimeMetrics()
                )
            )
            
        mappings = []
        overall_status = RuntimeExecutionStatus.COMPLETED
        metrics = RuntimeMetrics()
        
        try:
            for directive in directives:
                handle = self.adapter.dispatch_directive(directive)
                summary = self.adapter.get_execution_summary(handle)
                
                mappings.append(DirectiveExecutionMapping(
                    directive_id=directive.directive_id,
                    runtime_task_id=handle,
                    status=summary.overall_status
                ))
                
                if summary.overall_status != RuntimeExecutionStatus.COMPLETED:
                    overall_status = summary.overall_status
                    
                metrics.execution_time_ms += summary.metrics.execution_time_ms
                metrics.tasks_spawned += summary.metrics.tasks_spawned
                metrics.capabilities_invoked += summary.metrics.capabilities_invoked
                
            return RuntimeIntegrationResult(
                result_id=str(uuid.uuid4()),
                summary=ExecutionSummary(
                    summary_id=str(uuid.uuid4()),
                    overall_status=overall_status,
                    directive_mappings=mappings,
                    metrics=metrics
                )
            )
        except RuntimeIntegrationError:
            raise
        except Exception as e:
            raise RuntimeIntegrationError(f"Unexpected error in bridge: {str(e)}", "IntelligenceRuntimeBridge")
