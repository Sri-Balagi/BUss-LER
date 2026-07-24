from app.domain.cognition.models import AgentState, AgentStatus
from app.domain.intelligence.pipeline import IPipelineStep, PipelineContext, PipelineResult
from app.domain.intelligence.telemetry import IntelligenceMetrics


class ObserveStep(IPipelineStep[AgentState, AgentState]):
    """
    Step 1: Observe. Captures environmental state and updates the agent's context.
    """

    async def execute(self, context: PipelineContext[AgentState]) -> PipelineResult[AgentState]:
        agent_state = context.payload
        agent_state.status = AgentStatus.OBSERVING

        # In a real implementation, this would interact with IAgentImplementation to parse raw inputs
        # or capture Twin telemetry that has changed since the last iteration.

        return PipelineResult(
            context=context.execution_context,
            payload=agent_state,
            metrics=IntelligenceMetrics(duration_ms=1.0, token_usage={}, provider_metadata={})
        )
