from app.domain.cognition.models import AgentState, AgentStatus
from app.domain.intelligence.pipeline import IPipelineStep, PipelineContext, PipelineResult
from app.domain.intelligence.telemetry import IntelligenceMetrics


class ReasonStep(IPipelineStep[AgentState, AgentState]):
    """
    Step 3: Reason. Synthesizes knowledge into inferences/insights.
    """

    async def execute(self, context: PipelineContext[AgentState]) -> PipelineResult[AgentState]:
        agent_state = context.payload
        agent_state.status = AgentStatus.REASONING

        # Integration with Reasoning Engine

        return PipelineResult(
            context=context.execution_context,
            payload=agent_state,
            metrics=IntelligenceMetrics(duration_ms=1.0, token_usage={}, provider_metadata={})
        )
