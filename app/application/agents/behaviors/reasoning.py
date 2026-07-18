from typing import Optional
from app.domain.agents.behavior import IAgentBehavior
from app.domain.workflows.models import Task, TaskStatus
from app.domain.approval.models import Approval
from app.shared.events.models import ApprovalExpiredEvent
from app.domain.intelligence.platform import IIntelligencePlatform
from app.domain.intelligence.schemas import ReasoningResult
from app.domain.intelligence.prompts import TaskPrompt

class ReasoningBehavior(IAgentBehavior):
    def __init__(self, platform: IIntelligencePlatform):
        self._platform = platform

    async def execute(self, task: Task) -> Task:
        findings = task.inputs.get("findings", "")
        prompt = TaskPrompt("Reason over these findings: {findings}").render(findings=findings)
        result: ReasoningResult = await self._platform.generate_structured(prompt=prompt, schema=ReasoningResult)
        
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
