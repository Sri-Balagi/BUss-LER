from app.application.cognition.pipeline import CognitivePipeline
from app.application.intelligence.kernel import IntelligenceKernel
from app.domain.cognition.models import AgentState
from app.domain.intelligence.pipeline import PipelineContext


class CognitiveEngineService:
    """
    Coordinates cognitive execution through the Intelligence Kernel.
    """

    def __init__(
        self,
        kernel: IntelligenceKernel,
        pipeline: CognitivePipeline,
    ):
        self._kernel = kernel
        self._pipeline = pipeline

    async def execute_agent_loop(
        self,
        context: AgentState
    ) -> AgentState:
        """
        Executes the agent's cognitive pipeline until completion or terminal failure.
        """
        pipeline_context = PipelineContext(
            execution_context=context,
            payload=context
        )

        result = await self._kernel.pipeline_manager.run_pipeline(
            self._pipeline,
            pipeline_context
        )

        if not isinstance(result.payload, AgentState):
            raise RuntimeError("Cognitive pipeline did not return a valid AgentState")
        return result.payload
