import asyncio
import logging
import uuid
from typing import Optional

from app.application.intelligence.kernel import IntelligenceKernel
from app.domain.intelligence.pipeline import PipelineContext
from app.domain.cognition.events import LearningRequested
from app.domain.learning.models import LearningContext, LearningResult
from app.application.learning.steps.consolidation_step import ConsolidationStep


logger = logging.getLogger(__name__)


class LearningService:
    """
    Application service that asynchronously handles learning requests.
    Listens to the LearningRequested event from Agent Cognition and
    pipelines it through the Learning Consolidation step.
    """

    def __init__(self, kernel: IntelligenceKernel, consolidation_step: ConsolidationStep):
        self._kernel = kernel
        self._consolidation_step = consolidation_step

    async def initialize(self):
        """Initializes the service by subscribing to relevant events."""
        # Note: EventRouter currently doesn't expose subscribe directly for domain handlers easily, 
        # but in Wave 5 testing we use the EventBus.
        # Assuming the Kernel provides a way or we just use the EventBus.
        # For this implementation, we assume the host bootstraps this handler.
        pass

    async def handle_learning_requested(self, event: LearningRequested) -> Optional[LearningResult]:
        """
        Asynchronously handles the LearningRequested event.
        Executes the learning consolidation pipeline without blocking the cognition loop.
        """
        logger.info(f"handling_learning_requested agent_id={event.agent_id} iteration={event.iteration}")

        try:
            learning_context = LearningContext(
                agent_id=event.agent_id,
                tenant_id=event.tenant_id,
                iteration=event.iteration,
                feedback=event.feedback,
                correlation_id=event.correlation_id or str(uuid.uuid4())
            )

            pipeline_context = PipelineContext(
                execution_context=learning_context,
                payload=learning_context
            )

            result = await self._kernel.pipeline_manager.run_pipeline(
                self._consolidation_step,
                pipeline_context
            )
            
            logger.info(f"learning_pipeline_completed agent_id={event.agent_id} success={result.payload.success}")
            return result.payload

        except Exception as e:
            logger.error(f"learning_pipeline_failed agent_id={event.agent_id} error={e}")
            # LearningFailed is already published by the step on internal errors,
            # but if setup fails, we'd log it here.
            return None
