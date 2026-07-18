from typing import Dict, Any, Type, Optional, Callable, Awaitable
import logging

from app.domain.agents.behavior import IAgentBehavior
from app.domain.agents.interfaces import IAgentRegistry
from app.domain.workflows.models import Task, TaskStatus
from app.shared.enums import AgentType, PrincipalType, ParticipantRole
from app.shared.events.bus import EventBus
from app.domain.session.models import SessionParticipant
from app.domain.session.repository import ISessionRepository
from app.domain.tasks.repository import ITaskRepository

from app.shared.events.models import (
    TaskDelegatedEvent,
    TaskCompletedEvent,
    AgentStartedEvent,
    AgentCompletedEvent,
    AgentFailedEvent,
    AgentBlockedEvent,
    ApprovalApprovedEvent,
    ApprovalRejectedEvent,
    ApprovalExpiredEvent,
    WorkflowCompletedEvent
)

logger = logging.getLogger(__name__)

class AgentRuntime:
    """
    Stateless Event-Driven Agent Runtime for Wave 8.
    """
    def __init__(self, registry: IAgentRegistry, event_bus: EventBus, session_repo: ISessionRepository, task_repo: ITaskRepository):
        self._registry = registry
        self._event_bus = event_bus
        self._session_repo = session_repo
        self._task_repo = task_repo
        self._behaviors: Dict[AgentType, IAgentBehavior] = {}

    def register_behavior(self, agent_type: AgentType, behavior: IAgentBehavior) -> None:
        self._behaviors[agent_type] = behavior

    async def _add_agent_to_session(self, session_id: str, agent_id: str, tenant_id: Optional[str]) -> None:
        session = await self._session_repo.get_session(session_id, tenant_id)
        if session:
            # Check for duplicate
            if not any(p.id == agent_id and p.type == PrincipalType.AGENT for p in session.participants):
                session.participants.append(
                    SessionParticipant(
                        id=agent_id,
                        type=PrincipalType.AGENT,
                        role=ParticipantRole.CONTRIBUTOR
                    )
                )
                await self._session_repo.save_session(session)

    async def handle_task_delegated(self, event: TaskDelegatedEvent) -> None:
        """Handle execution of a newly delegated task."""
        task = await self._task_repo.get_task(event.task_id)
        if not task:
            logger.error(f"Task {event.task_id} not found in runtime state.")
            return

        agent = self._registry.get_agent(task.assigned_agent_id)
        if not agent:
            logger.error(f"Agent {task.assigned_agent_id} not found.")
            return
            
        behavior = self._behaviors.get(agent.agent_type)
        if not behavior:
            logger.error(f"No behavior registered for agent type {agent.agent_type}")
            return

        # Add agent to session
        await self._add_agent_to_session(task.execution_context.session_id, agent.id, task.execution_context.tenant_id)

        # Publish AgentStarted
        await self._event_bus.publish(AgentStartedEvent(
            correlation_id=event.correlation_id,
            agent_id=agent.id,
            tenant_id=task.execution_context.tenant_id,
            workflow_id=task.workflow_id,
            task_id=task.task_id,
            session_id=task.execution_context.session_id,
            principal_type=task.execution_context.principal_type,
            principal_id=task.execution_context.principal_id,
            trace_id=task.execution_context.trace_id
        ))

        try:
            task = await behavior.execute(task)
            await self._task_repo.save_task(task)

            if task.status == TaskStatus.COMPLETED:
                await self._event_bus.publish(AgentCompletedEvent(
                    correlation_id=event.correlation_id,
                    agent_id=agent.id,
                    tenant_id=task.execution_context.tenant_id,
                    workflow_id=task.workflow_id,
                    task_id=task.task_id,
                    session_id=task.execution_context.session_id,
                    principal_type=task.execution_context.principal_type,
                    principal_id=task.execution_context.principal_id,
                    trace_id=task.execution_context.trace_id
                ))
                await self._event_bus.publish(TaskCompletedEvent(
                    correlation_id=event.correlation_id,
                    workflow_id=task.workflow_id,
                    task_id=task.task_id,
                    session_id=task.execution_context.session_id,
                    principal_type=task.execution_context.principal_type,
                    principal_id=task.execution_context.principal_id,
                    trace_id=task.execution_context.trace_id,
                    outputs=task.outputs
                ))
            elif task.status == TaskStatus.BLOCKED_ON_APPROVAL:
                await self._event_bus.publish(AgentBlockedEvent(
                    correlation_id=event.correlation_id,
                    agent_id=agent.id,
                    tenant_id=task.execution_context.tenant_id,
                    workflow_id=task.workflow_id,
                    task_id=task.task_id,
                    session_id=task.execution_context.session_id,
                    principal_type=task.execution_context.principal_type,
                    principal_id=task.execution_context.principal_id,
                    trace_id=task.execution_context.trace_id,
                    reason="Waiting for Approval"
                ))

        except Exception as e:
            task.status = TaskStatus.FAILED
            await self._task_repo.save_task(task)
            await self._event_bus.publish(AgentFailedEvent(
                correlation_id=event.correlation_id,
                agent_id=agent.id,
                tenant_id=task.execution_context.tenant_id,
                reason=str(e),
                workflow_id=task.workflow_id,
                task_id=task.task_id,
                session_id=task.execution_context.session_id,
                principal_type=task.execution_context.principal_type,
                principal_id=task.execution_context.principal_id,
                trace_id=task.execution_context.trace_id
            ))

    async def handle_approval_approved(self, event: ApprovalApprovedEvent) -> None:
        # We need to find which task was blocked on this approval.
        # Assuming target_type == "task" and target_id == task_id
        if event.target_type != "task":
            return
            
        task = await self._task_repo.get_task(event.target_id)
        if not task or task.status != TaskStatus.BLOCKED_ON_APPROVAL:
            return

        agent = self._registry.get_agent(task.assigned_agent_id)
        behavior = self._behaviors.get(agent.agent_type)
        
        # We pass a dummy Approval for the interface, as the event tells us it's approved
        from app.domain.approval.models import Approval, ApprovalState
        approval = Approval(
            approval_id=event.approval_id,
            target_type=event.target_type,
            target_id=event.target_id,
            state=ApprovalState.APPROVED,
            requested_by=task.assigned_agent_id
        )

        try:
            task = await behavior.resume(task, approval)
            await self._task_repo.save_task(task)
            
            if task.status == TaskStatus.COMPLETED:
                await self._event_bus.publish(AgentCompletedEvent(
                    correlation_id=event.correlation_id,
                    agent_id=agent.id,
                    tenant_id=task.execution_context.tenant_id,
                    workflow_id=task.workflow_id,
                    task_id=task.task_id,
                    session_id=task.execution_context.session_id,
                    principal_type=task.execution_context.principal_type,
                    principal_id=task.execution_context.principal_id,
                    trace_id=task.execution_context.trace_id
                ))
                await self._event_bus.publish(TaskCompletedEvent(
                    correlation_id=event.correlation_id,
                    workflow_id=task.workflow_id,
                    task_id=task.task_id,
                    session_id=task.execution_context.session_id,
                    principal_type=task.execution_context.principal_type,
                    principal_id=task.execution_context.principal_id,
                    trace_id=task.execution_context.trace_id,
                    outputs=task.outputs
                ))
        except Exception as e:
            task.status = TaskStatus.FAILED
            await self._task_repo.save_task(task)
            await self._event_bus.publish(AgentFailedEvent(
                correlation_id=event.correlation_id,
                agent_id=agent.id,
                tenant_id=task.execution_context.tenant_id,
                reason=str(e),
                workflow_id=task.workflow_id,
                task_id=task.task_id,
                session_id=task.execution_context.session_id,
                principal_type=task.execution_context.principal_type,
                principal_id=task.execution_context.principal_id,
                trace_id=task.execution_context.trace_id
            ))

    async def handle_approval_rejected(self, event: ApprovalRejectedEvent) -> None:
        if event.target_type != "task":
            return
            
        task = await self._task_repo.get_task(event.target_id)
        if not task or task.status != TaskStatus.BLOCKED_ON_APPROVAL:
            return

        task.status = TaskStatus.FAILED
        await self._task_repo.save_task(task)
        
        await self._event_bus.publish(AgentFailedEvent(
            correlation_id=event.correlation_id,
            agent_id=task.assigned_agent_id,
            tenant_id=task.execution_context.tenant_id,
            reason="Approval Rejected",
            workflow_id=task.workflow_id,
            task_id=task.task_id,
            session_id=task.execution_context.session_id,
            principal_type=task.execution_context.principal_type,
            principal_id=task.execution_context.principal_id,
            trace_id=task.execution_context.trace_id
        ))

    async def handle_approval_expired(self, event: ApprovalExpiredEvent) -> None:
        if event.target_type != "task":
            return
            
        task = await self._task_repo.get_task(event.target_id)
        if not task:
            return

        # Planner needs to be notified. The planner agent behavior might need to handle this.
        # Since the task blocked is Executor, we need to notify the parent task (Planner).
        parent_task_id = task.parent_task_id
        if not parent_task_id:
            return
            
        parent_task = await self._task_repo.get_task(parent_task_id)
        if not parent_task:
            return
            
        agent = self._registry.get_agent(parent_task.assigned_agent_id)
        if agent:
            behavior = self._behaviors.get(agent.agent_type)
            if behavior:
                await behavior.handle_expiration(parent_task, event)

    async def handle_task_completed(self, event: TaskCompletedEvent) -> None:
        """Handle a subtask completion and notify the parent."""
        task = await self._task_repo.get_task(event.task_id)
        if not task:
            return

        parent_task_id = task.parent_task_id
        if not parent_task_id:
            # If the root task completes, the workflow is completed
            await self._event_bus.publish(WorkflowCompletedEvent(
                correlation_id=event.correlation_id,
                workflow_id=task.workflow_id,
                session_id=task.execution_context.session_id,
                principal_type=task.execution_context.principal_type,
                principal_id=task.execution_context.principal_id,
                trace_id=task.execution_context.trace_id,
                final_outputs=task.outputs
            ))
            return
            
        parent_task = await self._task_repo.get_task(parent_task_id)
        if not parent_task:
            return
            
        agent = self._registry.get_agent(parent_task.assigned_agent_id)
        if agent:
            behavior = self._behaviors.get(agent.agent_type)
            if behavior:
                updated_parent = await behavior.handle_subtask_completed(parent_task, event.task_id, event.outputs)
                await self._task_repo.save_task(updated_parent)
                
                # Check if parent is now completed
                if updated_parent.status == TaskStatus.COMPLETED:
                    await self._event_bus.publish(AgentCompletedEvent(
                        correlation_id=event.correlation_id,
                        agent_id=agent.id,
                        tenant_id=updated_parent.execution_context.tenant_id,
                        workflow_id=updated_parent.workflow_id,
                        task_id=updated_parent.task_id,
                        session_id=updated_parent.execution_context.session_id,
                        principal_type=updated_parent.execution_context.principal_type,
                        principal_id=updated_parent.execution_context.principal_id,
                        trace_id=updated_parent.execution_context.trace_id
                    ))
                    await self._event_bus.publish(TaskCompletedEvent(
                        correlation_id=event.correlation_id,
                        workflow_id=updated_parent.workflow_id,
                        task_id=updated_parent.task_id,
                        session_id=updated_parent.execution_context.session_id,
                        principal_type=updated_parent.execution_context.principal_type,
                        principal_id=updated_parent.execution_context.principal_id,
                        trace_id=updated_parent.execution_context.trace_id,
                        outputs=updated_parent.outputs
                    ))
