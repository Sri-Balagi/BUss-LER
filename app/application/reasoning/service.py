from uuid import UUID

from app.application.intelligence.kernel import IntelligenceKernel
from app.application.reasoning.pipeline import ReasoningPipeline
from app.domain.intelligence.context import IntelligenceContext
from app.domain.reasoning.models import ReasoningContext, ReasoningQuery, ReasoningResponse


class ReasoningEngineService:
    """Primary application service for issuing reasoning requests."""

    def __init__(self, kernel: IntelligenceKernel, pipeline: ReasoningPipeline):
        self._kernel = kernel
        self._pipeline = pipeline

    async def execute_reasoning(
        self,
        context: IntelligenceContext,
        query: ReasoningQuery,
        entity_id: UUID | None = None
    ) -> ReasoningResponse:

        # Build the reasoning context
        reasoning_context = ReasoningContext(
            tenant_id=context.tenant_id,
            user_id=context.user_id,
            session_id=context.session_id,
            workflow_id=context.workflow_id,
            conversation_id=context.conversation_id,
            trace_id=context.trace_id,
            correlation_id=context.correlation_id,
            permissions=context.permissions,
            metadata=context.metadata
        )

        # Package for pipeline execution
        from app.domain.intelligence.pipeline import PipelineContext

        # Pass entity_id and query via payload
        payload = {
            "query": query,
            "entity_id": entity_id
        }

        pipeline_ctx = PipelineContext(
            execution_context=reasoning_context,
            payload=payload
        )

        result = await self._kernel.pipeline_manager.run_pipeline(self._pipeline, pipeline_ctx)
        if not isinstance(result.payload, ReasoningResponse):
            raise RuntimeError("Reasoning pipeline did not return a valid ReasoningResponse")
        return result.payload
