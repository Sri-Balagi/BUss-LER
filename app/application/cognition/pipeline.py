import time
from typing import List

from app.domain.intelligence.pipeline import IIntelligencePipeline, IPipelineStep, PipelineContext, PipelineResult
from app.domain.cognition.models import AgentState, AgentStatus, ReflectionFeedback
from app.domain.cognition.events import CognitiveCycleStarted, CognitiveCycleCompleted
from app.application.intelligence.kernel import EventRouter
from app.domain.intelligence.telemetry import IntelligenceMetrics


class CognitivePipeline(IIntelligencePipeline[AgentState, AgentState]):
    """
    Orchestrates the cyclical execution of cognitive steps for an agent.
    Loops until ReflectionFeedback says IS_COMPLETE or max_iterations is reached.
    """
    
    def __init__(
        self,
        steps: List[IPipelineStep[AgentState, AgentState]],
        event_router: EventRouter,
        max_iterations: int = 5,
        max_execution_time: float = 60.0
    ):
        self._steps = steps
        self._event_router = event_router
        self._max_iterations = max_iterations
        self._max_execution_time = max_execution_time

    async def execute(self, context: PipelineContext[AgentState]) -> PipelineResult[AgentState]:
        start_time = time.perf_counter()
        agent_state: AgentState = context.payload
        
        while agent_state.current_iteration < self._max_iterations:
            agent_state.current_iteration += 1
            
            # Publish cycle start
            await self._event_router.publish(
                CognitiveCycleStarted(
                    agent_id=agent_state.agent_id,
                    tenant_id=agent_state.tenant_id,
                    iteration=agent_state.current_iteration,
                    correlation_id=agent_state.correlation_id,
                )
            )
            
            # Execute all steps sequentially
            for step in self._steps:
                # If execution time exceeded, abort
                if time.perf_counter() - start_time > self._max_execution_time:
                    agent_state.status = AgentStatus.FAILED
                    agent_state.reflection_feedback = ReflectionFeedback.FAILED
                    break
                    
                step_context = PipelineContext(
                    execution_context=agent_state,
                    payload=agent_state
                )
                step_result = await step.execute(step_context)
                agent_state = step_result.payload
                
            # Check terminal conditions
            if agent_state.status == AgentStatus.FAILED:
                break
                
            if agent_state.reflection_feedback == ReflectionFeedback.IS_COMPLETE:
                agent_state.status = AgentStatus.COMPLETED
                break
                
            if agent_state.reflection_feedback == ReflectionFeedback.FAILED:
                agent_state.status = AgentStatus.FAILED
                break
                
        # If we exit the loop and we haven't completed or failed, we probably hit max_iterations
        if agent_state.status not in (AgentStatus.COMPLETED, AgentStatus.FAILED):
            agent_state.status = AgentStatus.FAILED
            agent_state.reflection_feedback = ReflectionFeedback.FAILED
            
        # Publish cycle complete
        await self._event_router.publish(
            CognitiveCycleCompleted(
                agent_id=agent_state.agent_id,
                tenant_id=agent_state.tenant_id,
                iterations_run=agent_state.current_iteration,
                final_feedback=agent_state.reflection_feedback,
                correlation_id=agent_state.correlation_id,
            )
        )
            
        duration = time.perf_counter() - start_time
        metrics = IntelligenceMetrics(
            duration_ms=duration * 1000,
            token_usage={},
            provider_metadata={"iterations": agent_state.current_iteration}
        )
        
        return PipelineResult(
            context=agent_state,
            payload=agent_state,
            metrics=metrics
        )
