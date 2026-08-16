from app.domain.cognition.models import AgentState, AgentStatus
from app.domain.intelligence.pipeline import IPipelineStep, PipelineContext, PipelineResult
from app.domain.intelligence.telemetry import IntelligenceMetrics


class ExecuteStep(IPipelineStep[AgentState, AgentState]):
    """
    Step 5: Execute. Executes the current plan step and logs the outcome.
    """

    async def execute(self, context: PipelineContext[AgentState]) -> PipelineResult[AgentState]:
        agent_state = context.payload
        agent_state.status = AgentStatus.EXECUTING

        # Integration with ExecutionCoordinator (from Intelligence Kernel)
        # For Milestone 7, we just simulate an execution.
        agent_state.execution_history.append({"step": agent_state.current_iteration, "result": "success"})

        return PipelineResult(
            context=context.execution_context,
            payload=agent_state,
            metrics=IntelligenceMetrics(duration_ms=1.0, token_usage={}, provider_metadata={})
        )
