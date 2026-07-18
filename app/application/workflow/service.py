import structlog
from app.application.intelligence.kernel import PipelineManager
from app.domain.intelligence.pipeline import PipelineContext
from app.domain.workflow.models import WorkflowOptimizationContext
from app.application.workflow.steps.optimization_step import WorkflowOptimizationStep

logger = structlog.get_logger(__name__)


class WorkflowIntelligenceService:
    """Service facade for Workflow Intelligence pipeline executions."""
    
    def __init__(self, pipeline_manager: PipelineManager, optimization_step: WorkflowOptimizationStep):
        self._pipeline_manager = pipeline_manager
        self._optimization_step = optimization_step
        
    async def optimize_workflow(self, context: WorkflowOptimizationContext) -> WorkflowOptimizationContext:
        """Executes the workflow optimization pipeline on the given context."""
        logger.info("executing_workflow_optimization_pipeline", workflow_id=str(context.workflow.workflow_id))
        
        pipeline_context = PipelineContext(
            execution_context=context,
            payload=context
        )
        
        # We pass the step directly to the pipeline manager, as it implements execute()
        result_state = await self._pipeline_manager.run_pipeline(
            self._optimization_step,
            pipeline_context
        )
        
        logger.info("workflow_optimization_pipeline_completed", workflow_id=str(result_state.payload.workflow.workflow_id))
        return result_state.payload
