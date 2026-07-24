from app.domain.agents.behavior import IAgentBehavior
from app.domain.approval.models import Approval, ApprovalState
from app.domain.workflows.models import Task, TaskStatus
from app.shared.events.models import ApprovalExpiredEvent


class ExecutorBehavior(IAgentBehavior):
    async def execute(self, task: Task) -> Task:
        # Check if approval is required. For testing, we can simulate it's always required.
        needs_approval = task.inputs.get("needs_approval", True)

        if needs_approval:
            # We transition to blocked. The caller or the event bus would actually handle the event,
            # but here we just return the blocked task. In a real system we'd emit ApprovalRequestedEvent.
            task.status = TaskStatus.BLOCKED_ON_APPROVAL
        else:
            task.outputs["result"] = "Executed without approval."
            task.status = TaskStatus.COMPLETED

        return task

    async def resume(self, task: Task, approval: Approval) -> Task:
        if approval.state == ApprovalState.APPROVED:
            task.outputs["result"] = "Executed with approval."
            task.status = TaskStatus.COMPLETED
        else:
            task.status = TaskStatus.FAILED
            task.outputs["error"] = f"Approval was {approval.state}"

        return task

    async def handle_expiration(self, task: Task, event: ApprovalExpiredEvent) -> Task:
        task.status = TaskStatus.FAILED
        task.outputs["error"] = "Approval expired."
        return task

    async def handle_subtask_completed(self, task: Task, subtask_id: str, outputs: dict) -> Task:
        return task
