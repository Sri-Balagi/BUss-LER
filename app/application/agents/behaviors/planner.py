from typing import Optional, List
import uuid
import logging

from app.domain.agents.behavior import IAgentBehavior
from app.domain.workflows.models import Task, TaskStatus
from app.domain.approval.models import Approval
from app.shared.events.models import ApprovalExpiredEvent, TaskDelegatedEvent
from app.shared.enums import AgentType

from app.domain.tasks.repository import ITaskRepository

logger = logging.getLogger(__name__)

class PlannerBehavior(IAgentBehavior):
    def __init__(self, event_bus, registry, task_repo: ITaskRepository):
        self._event_bus = event_bus
        self._registry = registry
        self._task_repo = task_repo

    async def execute(self, task: Task) -> Task:
        # Step 1: Research, Step 2: Reasoning, Step 3: Executor
        task.inputs["plan_steps"] = [AgentType.RESEARCH, AgentType.REASONING, AgentType.EXECUTOR]
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
        
        await self._event_bus.publish(TaskDelegatedEvent(
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
