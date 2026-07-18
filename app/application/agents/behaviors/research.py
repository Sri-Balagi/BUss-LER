from typing import Optional
from app.domain.agents.behavior import IAgentBehavior
from app.domain.workflows.models import Task, TaskStatus
from app.domain.approval.models import Approval
from app.shared.events.models import ApprovalExpiredEvent
from app.domain.intelligence.platform import IIntelligencePlatform
from app.domain.intelligence.schemas import ResearchResult
from app.domain.intelligence.prompts import TaskPrompt

class ResearchBehavior(IAgentBehavior):
    def __init__(self, platform: IIntelligencePlatform):
        self._platform = platform

    async def execute(self, task: Task) -> Task:
        prompt = TaskPrompt("Conduct research on: {objective}").render(objective=task.objective)
        result: ResearchResult = await self._platform.generate_structured(prompt=prompt, schema=ResearchResult)
        
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
