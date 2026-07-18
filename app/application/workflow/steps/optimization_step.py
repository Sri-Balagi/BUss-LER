import time
from typing import Optional
import structlog

from app.domain.intelligence.capability import CapabilityType
from app.domain.intelligence.pipeline import IPipelineStep, PipelineContext, PipelineResult
from app.domain.workflow.events import (
    WorkflowOptimizationStarted,
    WorkflowOptimizationCompleted,
    WorkflowOptimizationFailed,
    WorkflowOptimized
)
from app.domain.workflow.models import (
    WorkflowOptimizationContext,
    IWorkflowIntelligenceProvider,
    WorkflowState,
    WorkflowOptimizationMetrics
)
from app.domain.intelligence.provider import ICapabilityRegistry
from app.application.intelligence.kernel import EventRouter


logger = structlog.get_logger(__name__)


class WorkflowOptimizationStep(IPipelineStep[WorkflowOptimizationContext, WorkflowOptimizationContext]):
    """Pipeline step that optimizes a workflow using an IWorkflowIntelligenceProvider."""
    
    def __init__(self, registry: ICapabilityRegistry, event_router: EventRouter):
        self._registry = registry
        self._event_router = event_router
        
    async def execute(
        self,
        context: PipelineContext[WorkflowOptimizationContext]
    ) -> PipelineResult[WorkflowOptimizationContext]:
        workflow_context = context.payload.model_copy(update={"state": WorkflowState.OPTIMIZING})
        start_time = time.time()
        
        # Publish Started event
        await self._event_router.publish(
            WorkflowOptimizationStarted(
                correlation_id=workflow_context.correlation_id,
                workflow_id=workflow_context.workflow.workflow_id
            )
        )
        
        try:
            # Resolve Optimizer capability
            provider = self._registry.resolve_provider(CapabilityType.WORKFLOW)
            if not provider:
                raise RuntimeError("No Workflow Intelligence Provider registered.")
            if not isinstance(provider, IWorkflowIntelligenceProvider):
                raise TypeError(f"Resolved provider {type(provider)} is not an IWorkflowIntelligenceProvider.")
                
            # Execute optimization
            result = await provider.optimize(workflow_context)
            
            end_time = time.time()
            elapsed_ms = (end_time - start_time) * 1000
            
            if result.success:
                workflow_context = workflow_context.model_copy(update={
                    "workflow": result.optimized_workflow,
                    "state": WorkflowState.COMPLETED
                })
                
                # Publish Optimized & Completed events
                await self._event_router.publish(
                    WorkflowOptimized(
                        correlation_id=workflow_context.correlation_id,
                        workflow_id=workflow_context.workflow.workflow_id,
                        tasks_optimized_count=result.metrics.tasks_optimized_count
                    )
                )
                await self._event_router.publish(
                    WorkflowOptimizationCompleted(
                        correlation_id=workflow_context.correlation_id,
                        workflow_id=workflow_context.workflow.workflow_id,
                        optimization_time_ms=elapsed_ms
                    )
                )
                
                return PipelineResult(
                    context=context.execution_context,
                    payload=workflow_context,
                    metrics=result.metrics
                )
            else:
                raise RuntimeError(result.error_message or "Optimization failed without specific error.")
                
        except Exception as e:
            workflow_context = workflow_context.model_copy(update={"state": WorkflowState.FAILED})
            logger.error("workflow_optimization_failed", error=str(e))
            await self._event_router.publish(
                WorkflowOptimizationFailed(
                    correlation_id=workflow_context.correlation_id,
                    workflow_id=workflow_context.workflow.workflow_id,
                    error_message=str(e)
                )
            )
            # We don't swallow exceptions in this step, let the PipelineManager or Service handle it
            raise
