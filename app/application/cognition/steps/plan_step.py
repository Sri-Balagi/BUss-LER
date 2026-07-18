from app.domain.intelligence.pipeline import IPipelineStep, PipelineContext, PipelineResult
from app.domain.cognition.models import AgentState, AgentStatus
from app.domain.intelligence.telemetry import IntelligenceMetrics


class PlanStep(IPipelineStep[AgentState, AgentState]):
    """
    Step 4: Plan. Translates inferences into actionable plans if replanning is needed.
    """
    
    async def execute(self, context: PipelineContext[AgentState]) -> PipelineResult[AgentState]:
        agent_state = context.payload
        agent_state.status = AgentStatus.PLANNING
        
        # Integration with Planning Engine
        
        return PipelineResult(
            context=context.execution_context,
            payload=agent_state,
            metrics=IntelligenceMetrics(duration_ms=1.0, token_usage={}, provider_metadata={})
        )
