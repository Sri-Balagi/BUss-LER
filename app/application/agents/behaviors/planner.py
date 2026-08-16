import logging
import uuid

from app.domain.agents.behavior import IAgentBehavior
from app.domain.approval.models import Approval
from app.domain.decisions.models import DecisionPolicy
from app.domain.decisions.platform import IDecisionPlatform
from app.domain.intelligence.platform import IIntelligencePlatform
from app.domain.intelligence.schemas import PlannerCandidatePlans
from app.domain.memory.models import MemoryRecord, MemorySource, MemoryType
from app.domain.memory.platform import IMemoryPlatform
from app.domain.tasks.repository import ITaskRepository
from app.domain.workflows.models import Task, TaskStatus
from app.shared.enums import AgentType
from app.shared.events.models import ApprovalExpiredEvent, TaskDelegatedEvent

logger = logging.getLogger(__name__)

class PlannerBehavior(IAgentBehavior):
    def __init__(self, event_bus, registry, task_repo: ITaskRepository, platform: IIntelligencePlatform, decision_platform: IDecisionPlatform, memory_platform: IMemoryPlatform):
        self._event_bus = event_bus
        self._registry = registry
        self._task_repo = task_repo
        self._platform = platform
        self._decision_platform = decision_platform
        self._memory_platform = memory_platform
        self._policy = DecisionPolicy(approval_threshold=0.8)

    async def execute(self, task: Task) -> Task:
        prompt = f"Create candidate execution plans for objective: {task.objective}"
        raw_result = await self._platform.generate_structured(prompt=prompt, schema=PlannerCandidatePlans)
        result = PlannerCandidatePlans.model_validate(raw_result)
        # Evaluate candidate plans
        options = [{"id": str(i), "plan_steps": p.plan_steps} for i, p in enumerate(result.candidates)]
        if not options:
            task.status = TaskStatus.FAILED
            return task

        decision = await self._decision_platform.evaluate_options(
            goal_id=uuid.uuid4(),
            context={"objective": task.objective},
            options=options
        )

        # Persist decision to memory
        memory = MemoryRecord(
            memory_type=MemoryType.TASK,
            source=MemorySource.AGENT,
            title=f"Decision for {task.objective}",
            content=f"Selected option {decision.selected_option} with confidence {decision.confidence}. Justification: {decision.justification}",
            workflow_id=task.workflow_id
        )
        await self._memory_platform.store(memory)

        # Metrics
        if task.execution_context and task.execution_context.decision_metrics is not None:
            metrics = task.execution_context.decision_metrics
            metrics["confidence"] = decision.confidence
            metrics["approval_required"] = decision.confidence < self._policy.approval_threshold

        if decision.confidence < self._policy.approval_threshold:
            task.status = TaskStatus.BLOCKED_ON_APPROVAL
            # Emit approval event
            from app.shared.events.models import ApprovalCreatedEvent
            self._event_bus.publish(ApprovalCreatedEvent(
                correlation_id=task.execution_context.correlation_id,
                approval_id=str(uuid.uuid4()),
                target_type="TASK",
                target_id=task.task_id,
                requested_by=task.assigned_agent_id
            ))
            return task

        selected_steps = decision.selected_option.get("plan_steps", []) if decision.selected_option else []

        # Map string agent names to AgentType enums
        plan_steps = []
        for step in selected_steps:
            try:
                plan_steps.append(AgentType(step.upper()))
            except ValueError:
                pass

        task.inputs["plan_steps"] = plan_steps
        task.inputs["current_step_index"] = 0

        # Start first step
        task.status = TaskStatus.IN_PROGRESS
        await self._delegate_next_step(task)

        return task

    async def _delegate_next_step(self, task: Task):
        steps = task.inputs.get("plan_steps", [])
        current_idx = task.inputs.get("current_step_index", 0)

        if current_idx >= len(steps):
            task.status = TaskStatus.COMPLETED
            return

        next_agent_type = steps[current_idx]
        agents = self._registry.find_by_type(next_agent_type)
        if not agents:
            logger.error(f"No agents found for type {next_agent_type}")
            task.status = TaskStatus.FAILED
            return

        assigned_agent = agents[0]

        subtask = Task(
            workflow_id=task.workflow_id,
            parent_task_id=task.task_id,
            assigned_agent_id=assigned_agent.id,
            objective=f"Execute {next_agent_type.value}",
            inputs=task.outputs, # Pass current outputs as inputs
            execution_context=task.execution_context # PERFECT PROPAGATION
        )

        await self._task_repo.save_task(subtask)

        task.inputs["pending_subtask"] = subtask.task_id

        self._event_bus.publish(TaskDelegatedEvent(
            correlation_id=task.execution_context.correlation_id,
            delegator_id=task.assigned_agent_id,
            delegatee_id=assigned_agent.id,
            task_description=subtask.objective,
            task_id=subtask.task_id,
            workflow_id=task.workflow_id,
            session_id=task.execution_context.session_id,
            principal_type=task.execution_context.principal_type,
            principal_id=task.execution_context.principal_id
        ))

    async def resume(self, task: Task, approval: Approval) -> Task:
        from app.domain.approval.models import ApprovalState
        from app.domain.decisions.models import ReplanReason

        if approval.state == ApprovalState.APPROVED:
            # Continue with current plan
            task.status = TaskStatus.IN_PROGRESS
            await self._delegate_next_step(task)
        elif approval.state == ApprovalState.REJECTED:
            # Replan
            task.outputs["replan_reason"] = ReplanReason.APPROVAL_REJECTED.value
            task.objective = task.objective + f" (Avoid previously rejected plan, reason: {approval.reason})"
            # Restart planning
            return await self.execute(task)

        return task

    async def handle_expiration(self, task: Task, event: ApprovalExpiredEvent) -> Task:
        task.outputs["error"] = "Workflow aborted due to approval expiration."
        task.status = TaskStatus.FAILED
        return task

    async def handle_subtask_completed(self, task: Task, subtask_id: str, outputs: dict) -> Task:
        # Merge outputs
        task.outputs.update(outputs)

        # Advance step
        current_idx = task.inputs.get("current_step_index", 0)
        task.inputs["current_step_index"] = current_idx + 1

        await self._delegate_next_step(task)

        return task
