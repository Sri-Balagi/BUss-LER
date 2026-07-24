import time
from typing import Any

import structlog

from app.intelligence.core.session.session import CognitiveSession
from app.intelligence.executive.workflow import Workflow, WorkflowTask
from app.intelligence.pipeline.phases import (
    IPhase,
    PhaseResult,
    PhaseResultStatus,
    PipelinePhase,
)

logger = structlog.get_logger(__name__)


class ExecutePhase(IPhase):
    """Phase that executes the Workflow DAG using the WorkflowEngine."""

    def __init__(self, workflow_engine: Any) -> None:
        self.workflow_engine = workflow_engine

    @property
    def phase_type(self) -> PipelinePhase:
        return PipelinePhase.EXECUTE

    async def execute(self, session: CognitiveSession) -> PhaseResult:
        start = time.time()

        # In a real system, the 'workflow' would be retrieved from session state or
        # the PlanPhase artifact. For this Wave-1 stub, we create a dummy workflow.
        workflow = Workflow()
        workflow.add_task(WorkflowTask(capability_id="web_research", payload={"query": "test"}))

        try:
            workflow_result = await self.workflow_engine.execute_workflow(workflow, session.session_id)

            return PhaseResult(
                phase=self.phase_type,
                status=PhaseResultStatus.SUCCESS if workflow_result.success else PhaseResultStatus.FAILED,
                artifact=workflow_result,
                duration_ms=(time.time() - start) * 1000
            )
        except Exception as e:
            return PhaseResult(
                phase=self.phase_type,
                status=PhaseResultStatus.FAILED,
                error_message=str(e),
                duration_ms=(time.time() - start) * 1000
            )


class ReflectPhase(IPhase):
    """Analyzes execution results to determine success/failure drivers."""

    @property
    def phase_type(self) -> PipelinePhase:
        return PipelinePhase.REFLECT

    async def execute(self, session: CognitiveSession) -> PhaseResult:
        start = time.time()
        logger.debug("ReflectPhase executing")

        # M10 Stub: Extract heuristics from execution history
        report = {"reflection": "Task succeeded quickly. Capability web_research performed well."}

        return PhaseResult(
            phase=self.phase_type,
            status=PhaseResultStatus.SUCCESS,
            artifact=report,
            duration_ms=(time.time() - start) * 1000
        )


class LearnPhase(IPhase):
    """Commits reflections as generalized heuristics to the knowledge base."""

    def __init__(self, knowledge_repository: Any = None) -> None:
        self.knowledge_repository = knowledge_repository

    @property
    def phase_type(self) -> PipelinePhase:
        return PipelinePhase.LEARN

    async def execute(self, session: CognitiveSession) -> PhaseResult:
        start = time.time()
        logger.debug("LearnPhase executing")

        # M10 Stub: Persist heuristics
        if self.knowledge_repository:
            # We mock the creation of a KnowledgeArtifact here.
            # In full pipeline, this comes from the ReflectPhase artifact.
            # self.knowledge_repository.store_artifact(...)
            pass

        return PhaseResult(
            phase=self.phase_type,
            status=PhaseResultStatus.SUCCESS,
            artifact={"heuristics_saved": 1},
            duration_ms=(time.time() - start) * 1000
        )
