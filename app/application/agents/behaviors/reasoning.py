from app.application.memory.context import ContextBuilder
from app.application.memory.retriever import MemoryRetriever
from app.domain.agents.behavior import IAgentBehavior
from app.domain.approval.models import Approval
from app.domain.intelligence.platform import IIntelligencePlatform
from app.domain.intelligence.prompts import TaskPrompt
from app.domain.intelligence.schemas import ReasoningResult
from app.domain.memory.models import MemoryRecord, MemorySource, MemoryType
from app.domain.memory.platform import IMemoryPlatform
from app.domain.workflows.models import Task, TaskStatus
from app.shared.events.models import ApprovalExpiredEvent


class ReasoningBehavior(IAgentBehavior):
    def __init__(self, platform: IIntelligencePlatform, retriever: MemoryRetriever, context_builder: ContextBuilder, memory_platform: IMemoryPlatform):
        self._platform = platform
        self._retriever = retriever
        self._context_builder = context_builder
        self._memory_platform = memory_platform

    async def execute(self, task: Task) -> Task:
        findings = task.inputs.get("findings", "")

        # Retrieve context
        retrieval_result = await self._retriever.retrieve(findings)
        context = await self._context_builder.build_context([retrieval_result])

        # Store metrics in ExecutionContext
        if task.execution_context and task.execution_context.memory_metrics is not None:
            metrics = task.execution_context.memory_metrics
            metrics["retrieval_latency"] = retrieval_result.latency
            metrics["memory_hits"] = retrieval_result.hit_count
            metrics["retrieval_strategy"] = retrieval_result.strategy

        prompt = TaskPrompt("Context: {context}\nReason over these findings: {findings}").render(context=context, findings=findings)
        raw_result = await self._platform.generate_structured(prompt=prompt, schema=ReasoningResult)
        result = ReasoningResult.model_validate(raw_result)

        # Store result in memory
        memory = MemoryRecord(
            memory_type=MemoryType.TASK,
            source=MemorySource.AGENT,
            title=f"Reasoning on {task.objective}",
            content="\n".join(result.observations + result.recommendations),
            workflow_id=task.workflow_id
        )
        await self._memory_platform.store(memory)

        task.outputs["recommendations"] = result.recommendations
        task.outputs["observations"] = result.observations
        task.outputs["risks"] = result.risks
        task.status = TaskStatus.COMPLETED
        return task

    async def resume(self, task: Task, approval: Approval) -> Task:
        return task

    async def handle_expiration(self, task: Task, event: ApprovalExpiredEvent) -> Task:
        return task

    async def handle_subtask_completed(self, task: Task, subtask_id: str, outputs: dict) -> Task:
        return task
