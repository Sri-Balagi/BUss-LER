import logging
from typing import Any

from app.domain.agents.interfaces import IAgentRegistry, IAgentRuntime
from app.shared.events.bus import EventBus
from app.domain.session.models import ParticipantRole, PrincipalType, SessionParticipant
from app.domain.session.repository import ISessionRepository

from app.domain.approval.models import Approval, ApprovalState
from app.domain.tasks.repository import ITaskRepository
from app.domain.workflows.models import TaskStatus
from app.shared.events.models import (
    AgentBlockedEvent,
    AgentCompletedEvent,
    AgentFailedEvent,
    AgentStartedEvent,
    ApprovalApprovedEvent,
    ApprovalExpiredEvent,
    ApprovalRejectedEvent,
    TaskCompletedEvent,
    TaskDelegatedEvent,
    WorkflowCompletedEvent,
)
from app.domain.goals.models import GoalState

logger = logging.getLogger(__name__)


class AgentRuntime(IAgentRuntime):
    """Runtime execution orchestrator for autonomous agent behaviors."""

    def __init__(
        self,
        event_bus: Any = None,
        registry: Any = None,
        task_repo: Any = None,
        session_repo: Any = None,
        behaviors: dict | None = None,
        goal_lifecycle_service: Any = None,
        reasoning_service: Any = None,
        planning_service: Any = None,
        workflow_service: Any = None,
        observation_service: Any = None,
        replanning_service: Any = None,
    ):
        from app.application.agents.registry import InMemoryAgentRegistry
        from app.application.agents.services.goal_lifecycle import (
            GoalLifecycleService,
            ReasoningService,
            PlanningService,
            ObservationService,
            ReplanningService,
        )
        from app.application.observation.engine import ObservationEngine
        from app.domain.tasks.repository import InMemoryTaskRepository
        from app.infrastructure.session.memory import InMemorySessionRepository

        args = [arg for arg in [event_bus, registry, task_repo, session_repo] if arg is not None]
        
        eb, reg, trepo, srepo = None, None, None, None
        for arg in args:
            if hasattr(arg, "publish") or hasattr(arg, "subscribe"):
                eb = arg
            elif hasattr(arg, "get_agent") or hasattr(arg, "register_agent") or hasattr(arg, "agents"):
                reg = arg
            elif hasattr(arg, "get_task") or hasattr(arg, "save_task") or hasattr(arg, "tasks"):
                trepo = arg
            elif hasattr(arg, "get_session") or hasattr(arg, "save_session") or hasattr(arg, "sessions"):
                srepo = arg

        self._event_bus = eb
        self._registry = reg or InMemoryAgentRegistry()
        self._task_repo = trepo or InMemoryTaskRepository()
        self._session_repo = srepo or InMemorySessionRepository()
        self._behaviors = behaviors or {}

        self._goal_lifecycle_service = goal_lifecycle_service or GoalLifecycleService()
        self._reasoning_service = reasoning_service or ReasoningService()
        self._planning_service = planning_service or PlanningService()
        self._workflow_service = workflow_service
        self._observation_service = observation_service or ObservationService(ObservationEngine())
        self._replanning_service = replanning_service or ReplanningService(self._planning_service)

    def register_behavior(self, agent_type: Any, behavior: Any) -> None:
        self._behaviors[agent_type] = behavior

    async def _add_agent_to_session(self, session_id: str, agent_id: str, tenant_id: str | None) -> None:
        session = await self._session_repo.get_session(session_id, tenant_id)
        if session:
            if not any(p.id == agent_id and p.type == PrincipalType.AGENT for p in session.participants):
                session.participants.append(
                    SessionParticipant(
                        id=agent_id,
                        type=PrincipalType.AGENT,
                        role=ParticipantRole.CONTRIBUTOR
                    )
                )
                await self._session_repo.save_session(session)

    async def spawn_agent(self, name: str, template: Any | None = None, capabilities: list[Any] | None = None) -> Any:
        from app.domain.agents.models import Agent
        from app.shared.enums import AgentStatus
        import uuid
        
        agent = Agent(
            id=str(uuid.uuid4()),
            template_id=template.id if template else None,
            name=name,
            description=template.description if template else f"Agent {name}",
            status=AgentStatus.REGISTERED,
            capabilities=capabilities or (template.capabilities if template else []),
            metadata={"role": template.role if template else "General"}
        )
        self._registry.register_agent(agent)
        return agent

    async def delegate_task(self, from_agent_id: str, to_agent_id: str, task_description: str) -> dict:
        from_agent = self._registry.get_agent(from_agent_id)
        to_agent = self._registry.get_agent(to_agent_id)
        if not from_agent or not to_agent:
            raise ValueError("Agent not found for delegation.")
        
        # Stub implementation for orchestration boundaries
        return {"status": "delegated", "from": from_agent_id, "to": to_agent_id, "task": task_description}

    async def execute_goal(self, agent_id: str, goal_description: str) -> dict:
        agent = self._registry.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")

        # Step 1: Create goal
        goal = await self._goal_lifecycle_service.create_goal(
            title=goal_description, description=goal_description, owner=agent_id
        )

        # Step 2: Reasoning
        await self._goal_lifecycle_service.update_state(goal, GoalState.REASONING)
        reasoning_output = await self._reasoning_service.reason(goal)

        # Step 3: Planning
        await self._goal_lifecycle_service.update_state(goal, GoalState.PLANNING)
        workflow = await self._planning_service.plan(goal, reasoning_output)

        # Step 4: Execution
        await self._goal_lifecycle_service.update_state(goal, GoalState.EXECUTING)
        if not self._workflow_service:
            await self._goal_lifecycle_service.update_state(goal, GoalState.COMPLETED)
            return {
                "status": "submitted",
                "agent_id": agent_id,
                "goal": goal_description,
                "goal_id": str(goal.goal_id),
                "state": goal.state.value,
                "history": goal.history,
            }

        wf_result = await self._workflow_service.execute_workflow(workflow, session_id=f"goal_{goal.goal_id}")

        # Step 5: Observation
        observation = await self._observation_service.observe(wf_result, goal)

        # Step 6: Re-planning loop
        iteration = 1
        while observation.should_replan and iteration < 5:
            await self._goal_lifecycle_service.update_state(goal, GoalState.REPLANNING)
            replanned_wf = await self._replanning_service.replan(
                goal, observation, workflow, max_iterations=5, current_iteration=iteration
            )
            if not replanned_wf:
                break
            await self._goal_lifecycle_service.update_state(goal, GoalState.EXECUTING)
            wf_result = await self._workflow_service.execute_workflow(replanned_wf, session_id=f"goal_{goal.goal_id}")
            observation = await self._observation_service.observe(wf_result, goal)
            workflow = replanned_wf
            iteration += 1

        if observation.should_replan:
            await self._goal_lifecycle_service.update_state(goal, GoalState.FAILED)
        else:
            await self._goal_lifecycle_service.update_state(goal, GoalState.COMPLETED)

        return {
            "status": goal.state.value,
            "agent_id": agent_id,
            "goal": goal_description,
            "goal_id": str(goal.goal_id),
            "state": goal.state.value,
            "history": goal.history,
            "metrics": observation.metrics,
        }

    async def get_agent_state(self, agent_id: str) -> dict:
        agent = self._registry.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        return {"agent_id": agent_id, "name": agent.name, "status": "idle"}

    def _get_agent_behavior(self, agent: Any) -> Any | None:
        primary_capability = agent.capabilities[0] if getattr(agent, "capabilities", None) else getattr(agent, "agent_type", None)
        behavior = self._behaviors.get(primary_capability)
        if not behavior and getattr(agent, "agent_type", None):
            behavior = self._behaviors.get(agent.agent_type)
        return behavior

    async def handle_task_delegated(self, event: TaskDelegatedEvent) -> None:
        """Handle execution of a newly delegated task."""
        if not event.task_id:
            return
        task = await self._task_repo.get_task(event.task_id)
        if not task:
            logger.error(f"Task {event.task_id} not found in runtime state.")
            return

        agent = self._registry.get_agent(task.assigned_agent_id)
        if not agent:
            logger.error(f"Agent {task.assigned_agent_id} not found.")
            return

        behavior = self._get_agent_behavior(agent)
        if not behavior:
            logger.error(f"No behavior registered for agent {agent.id}")
            return

        await self._add_agent_to_session(task.execution_context.session_id, agent.id, task.execution_context.tenant_id)

        self._event_bus.publish(AgentStartedEvent(
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
                self._event_bus.publish(AgentCompletedEvent(
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
                self._event_bus.publish(TaskCompletedEvent(
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
                self._event_bus.publish(AgentBlockedEvent(
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
            self._event_bus.publish(AgentFailedEvent(
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
        if event.target_type != "task":
            return

        task = await self._task_repo.get_task(event.target_id)
        if not task or task.status != TaskStatus.BLOCKED_ON_APPROVAL:
            return

        agent = self._registry.get_agent(task.assigned_agent_id)
        if not agent:
            return
        behavior = self._get_agent_behavior(agent)
        if not behavior:
            return

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
                self._event_bus.publish(AgentCompletedEvent(
                    correlation_id=event.correlation_id,
                    agent_id=str(agent.id),
                    tenant_id=str(task.execution_context.tenant_id) if task.execution_context and task.execution_context.tenant_id else None,
                ))
                self._event_bus.publish(TaskCompletedEvent(
                    correlation_id=event.correlation_id,
                    workflow_id=task.workflow_id,
                    task_id=task.task_id,
                    session_id=task.execution_context.session_id,
                    principal_type=task.execution_context.principal_type,
                    principal_id=task.execution_context.principal_id,
                    outputs=task.outputs
                ))
        except Exception as e:
            task.status = TaskStatus.FAILED
            await self._task_repo.save_task(task)
            self._event_bus.publish(AgentFailedEvent(
                correlation_id=event.correlation_id,
                agent_id=str(agent.id) if agent else "",
                tenant_id=str(task.execution_context.tenant_id) if task.execution_context and task.execution_context.tenant_id else None,
                reason=str(e),
            ))

    async def handle_approval_rejected(self, event: ApprovalRejectedEvent) -> None:
        if event.target_type != "task":
            return

        task = await self._task_repo.get_task(event.target_id)
        if not task or task.status != TaskStatus.BLOCKED_ON_APPROVAL:
            return

        task.status = TaskStatus.FAILED
        await self._task_repo.save_task(task)

        self._event_bus.publish(AgentFailedEvent(
            correlation_id=event.correlation_id,
            agent_id=str(task.assigned_agent_id) if task.assigned_agent_id else "",
            tenant_id=str(task.execution_context.tenant_id) if task.execution_context and task.execution_context.tenant_id else None,
            reason="Approval Rejected",
        ))

    async def handle_approval_expired(self, event: ApprovalExpiredEvent) -> None:
        if event.target_type != "task":
            return

        task = await self._task_repo.get_task(event.target_id)
        if not task:
            return

        parent_task_id = task.parent_task_id
        if not parent_task_id:
            return

        parent_task = await self._task_repo.get_task(parent_task_id)
        if not parent_task:
            return

        agent = self._registry.get_agent(parent_task.assigned_agent_id)
        if agent:
            behavior = self._get_agent_behavior(agent)
            if behavior:
                await behavior.handle_expiration(parent_task, event)

    async def handle_task_completed(self, event: TaskCompletedEvent) -> None:
        """Handle a subtask completion and notify the parent."""
        task = await self._task_repo.get_task(event.task_id)
        if not task:
            return

        parent_task_id = task.parent_task_id
        if not parent_task_id:
            self._event_bus.publish(WorkflowCompletedEvent(
                correlation_id=event.correlation_id,
                workflow_id=task.workflow_id,
                session_id=task.execution_context.session_id,
                principal_type=task.execution_context.principal_type,
                principal_id=task.execution_context.principal_id,
                final_outputs=task.outputs
            ))
            return

        parent_task = await self._task_repo.get_task(parent_task_id)
        if not parent_task:
            return

        agent = self._registry.get_agent(parent_task.assigned_agent_id)
        if agent:
            behavior = self._get_agent_behavior(agent)
            if behavior:
                updated_parent = await behavior.handle_subtask_completed(parent_task, event.task_id, event.outputs or {})
                await self._task_repo.save_task(updated_parent)

                if updated_parent.status == TaskStatus.COMPLETED:
                    self._event_bus.publish(AgentCompletedEvent(
                        correlation_id=event.correlation_id,
                        agent_id=str(agent.id),
                        tenant_id=str(updated_parent.execution_context.tenant_id) if updated_parent.execution_context and updated_parent.execution_context.tenant_id else None,
                    ))
                    self._event_bus.publish(TaskCompletedEvent(
                        correlation_id=event.correlation_id,
                        workflow_id=updated_parent.workflow_id,
                        task_id=updated_parent.task_id,
                        session_id=updated_parent.execution_context.session_id,
                        principal_type=updated_parent.execution_context.principal_type,
                        principal_id=updated_parent.execution_context.principal_id,
                        outputs=updated_parent.outputs
                    ))
