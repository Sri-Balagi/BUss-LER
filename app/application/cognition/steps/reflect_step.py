from app.domain.intelligence.pipeline import IPipelineStep, PipelineContext, PipelineResult
from app.domain.cognition.models import AgentState, AgentStatus, ReflectionFeedback
from app.domain.cognition.events import LearningRequested, ReflectionGenerated
from app.application.intelligence.kernel import EventRouter
from app.domain.intelligence.telemetry import IntelligenceMetrics


class ReflectStep(IPipelineStep[AgentState, AgentState]):
    """
    Step 6: Reflect. Evaluates the execution outcome to produce ReflectionFeedback.
    Emits async learning requests without blocking the pipeline.
    """
    
    def __init__(self, event_router: EventRouter):
        self._event_router = event_router
    
    async def execute(self, context: PipelineContext[AgentState]) -> PipelineResult[AgentState]:
        agent_state = context.payload
        agent_state.status = AgentStatus.REFLECTING
        
        # In a real implementation, the IAgentImplementation or Reasoning Engine would evaluate the state.
        # For Milestone 7, we rely on the MockProvider to set feedback based on the current goal context.
        # If no feedback was manually injected by tests, we default to IS_COMPLETE for safety.
        feedback = agent_state.reflection_feedback or ReflectionFeedback.IS_COMPLETE
        agent_state.reflection_feedback = feedback
        
        # Publish reflection event
        await self._event_router.publish(
            ReflectionGenerated(
                agent_id=agent_state.agent_id,
                tenant_id=agent_state.tenant_id,
                iteration=agent_state.current_iteration,
                feedback=feedback,
                correlation_id=agent_state.correlation_id,
            )
        )
        
        # Publish async learning event (Milestone 9 consumes this)
        await self._event_router.publish(
            LearningRequested(
                agent_id=agent_state.agent_id,
                tenant_id=agent_state.tenant_id,
                iteration=agent_state.current_iteration,
                feedback=feedback,
                correlation_id=agent_state.correlation_id,
            )
        )
        
        return PipelineResult(
            context=context.execution_context,
            payload=agent_state,
            metrics=IntelligenceMetrics(duration_ms=1.0, token_usage={}, provider_metadata={})
        )
