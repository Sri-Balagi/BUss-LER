import time
import uuid

from app.domain.intelligence.capability import CapabilityType
from app.domain.intelligence.pipeline import PipelineContext, PipelineResult, IPipelineStep
from app.application.intelligence.kernel import IntelligenceKernel
from app.domain.learning.models import LearningContext, LearningResult
from app.domain.learning.provider import ILearningProvider
from app.domain.learning.events import (
    LearningStarted,
    LearningCompleted,
    LearningFailed,
    KnowledgeExtracted,
    KnowledgeConsolidated
)

from app.domain.intelligence.provider import ICapabilityRegistry
from app.application.intelligence.kernel import EventRouter

class ConsolidationStep(IPipelineStep[LearningContext, LearningResult]):
    """
    Pipeline step for learning and knowledge consolidation.
    Resolves the ILearningProvider and executes consolidation.
    """

    def __init__(self, registry: ICapabilityRegistry, event_router: EventRouter):
        self._registry = registry
        self._event_router = event_router

    @property
    def name(self) -> str:
        return "LearningConsolidation"

    async def execute(self, context: PipelineContext[LearningContext]) -> PipelineResult[LearningResult]:
        learning_context = context.payload
        correlation_id = learning_context.correlation_id

        # Publish LearningStarted
        await self._event_router.publish(
            LearningStarted(
                event_id=uuid.uuid4(),
                correlation_id=correlation_id,
                agent_id=learning_context.agent_id,
                tenant_id=learning_context.tenant_id,
                iteration=learning_context.iteration
            )
        )

        try:
            # Resolve the active learning provider
            provider = self._registry.resolve_provider(CapabilityType.LEARNING)
            if not provider:
                raise RuntimeError("No Learning Provider registered.")

            # Consolidate knowledge
            result = await provider.consolidate_knowledge(learning_context)

            # Publish fine-grained events based on result
            if result.metrics.items_consolidated > 0:
                await self._event_router.publish(
                    KnowledgeExtracted(
                        event_id=uuid.uuid4(),
                        correlation_id=correlation_id,
                        agent_id=learning_context.agent_id,
                        tenant_id=learning_context.tenant_id,
                        extracted_items_count=result.metrics.items_consolidated
                    )
                )

                await self._event_router.publish(
                    KnowledgeConsolidated(
                        event_id=uuid.uuid4(),
                        correlation_id=correlation_id,
                        agent_id=learning_context.agent_id,
                        tenant_id=learning_context.tenant_id,
                        consolidated_items_count=result.metrics.items_consolidated
                    )
                )

            # Publish LearningCompleted
            await self._event_router.publish(
                LearningCompleted(
                    event_id=uuid.uuid4(),
                    correlation_id=correlation_id,
                    agent_id=learning_context.agent_id,
                    tenant_id=learning_context.tenant_id,
                    iteration=learning_context.iteration,
                    result=result
                )
            )

            return PipelineResult(
                context=learning_context,
                payload=result,
                metrics=result.metrics
            )

        except Exception as e:
            # Publish LearningFailed
            await self._event_router.publish(
                LearningFailed(
                    event_id=uuid.uuid4(),
                    correlation_id=correlation_id,
                    agent_id=learning_context.agent_id,
                    tenant_id=learning_context.tenant_id,
                    iteration=learning_context.iteration,
                    error=str(e)
                )
            )
            raise
