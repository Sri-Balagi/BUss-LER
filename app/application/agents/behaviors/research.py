from typing import Optional
from app.domain.agents.behavior import IAgentBehavior
from app.domain.workflows.models import Task, TaskStatus
from app.domain.approval.models import Approval
from app.shared.events.models import ApprovalExpiredEvent
from app.domain.intelligence.platform import IIntelligencePlatform
from app.domain.intelligence.schemas import ResearchResult
from app.domain.intelligence.prompts import TaskPrompt
from app.application.memory.retriever import MemoryRetriever
from app.application.memory.context import ContextBuilder
from app.domain.memory.platform import IMemoryPlatform
from app.domain.memory.models import MemoryRecord, MemoryType, MemorySource

class ResearchBehavior(IAgentBehavior):
    def __init__(self, platform: IIntelligencePlatform, retriever: MemoryRetriever, context_builder: ContextBuilder, memory_platform: IMemoryPlatform):
        self._platform = platform
        self._retriever = retriever
        self._context_builder = context_builder
        self._memory_platform = memory_platform

    async def execute(self, task: Task) -> Task:
        # Retrieve context
        retrieval_result = await self._retriever.retrieve(task.objective)
        context = await self._context_builder.build_context([retrieval_result])
        
        # Store metrics in ExecutionContext
        if task.execution_context and hasattr(task.execution_context, "memory_metrics"):
            metrics = task.execution_context.memory_metrics
            metrics["retrieval_latency"] = retrieval_result.latency
            metrics["memory_hits"] = retrieval_result.hit_count
            metrics["retrieval_strategy"] = retrieval_result.strategy
            
        prompt = TaskPrompt("Context: {context}\nConduct research on: {objective}").render(context=context, objective=task.objective)
        result: ResearchResult = await self._platform.generate_structured(prompt=prompt, schema=ResearchResult)
        
        # Store result in memory
        memory = MemoryRecord(
            memory_type=MemoryType.TASK,
            source=MemorySource.AGENT,
            title=f"Research on {task.objective}",
            content=result.findings,
            workflow_id=task.workflow_id
        )
        await self._memory_platform.store(memory)
        
        task.outputs["findings"] = result.findings
        task.outputs["sources"] = result.sources
        task.outputs["confidence"] = result.confidence
        task.status = TaskStatus.COMPLETED
        return task
        
    async def resume(self, task: Task, approval: Approval) -> Task:
        # Research agent doesn't pause for approvals in this flow
        return task
        
    async def handle_expiration(self, task: Task, event: ApprovalExpiredEvent) -> Task:
        return task
        
    async def handle_subtask_completed(self, task: Task, subtask_id: str, outputs: dict) -> Task:
        return task
