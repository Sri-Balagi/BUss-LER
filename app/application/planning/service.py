from typing import Optional

from app.domain.intelligence.pipeline import PipelineContext
from app.domain.planning.models import Goal, Plan, PlanningContext
from app.application.intelligence.kernel import IntelligenceKernel
from app.application.planning.pipeline import PlanningPipeline


class PlanningEngineService:
    """
    Coordinates planning execution through the Intelligence Kernel.
    """
    
    def __init__(
        self,
        kernel: IntelligenceKernel,
        pipeline: PlanningPipeline,
    ):
        self._kernel = kernel
        self._pipeline = pipeline

    async def create_plan(
        self, 
        context: PlanningContext, 
        goal: Goal
    ) -> Plan:
        """
        Creates and validates a plan for a given goal.
        Delegates the actual execution to the IntelligenceKernel's PipelineManager.
        """
        pipeline_context = PipelineContext(
            execution_context=context,
            payload=goal
        )
        
        result = await self._kernel.pipeline_manager.run_pipeline(
            self._pipeline,
            pipeline_context
        )
        
        return result.payload
