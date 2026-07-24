from app.domain.cognition.models import AgentState, AgentStatus
from app.domain.intelligence.pipeline import IPipelineStep, PipelineContext, PipelineResult
from app.domain.intelligence.telemetry import IntelligenceMetrics


class RetrieveStep(IPipelineStep[AgentState, AgentState]):
    """
    Step 2: Retrieve. Fetches relevant context using the RetrievalEngine.
    """

    async def execute(self, context: PipelineContext[AgentState]) -> PipelineResult[AgentState]:
        agent_state = context.payload
        agent_state.status = AgentStatus.RETRIEVING

        # Integration with Retrieval Pipeline would happen here.
        # For Milestone 7, we just simulate updating the context based on observation.

        return PipelineResult(
            context=context.execution_context,
            payload=agent_state,
            metrics=IntelligenceMetrics(duration_ms=1.0, token_usage={}, provider_metadata={})
        )
