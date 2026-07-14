import logging
from enum import StrEnum

from app.runtime.agents.context import AgentContext
from app.runtime.agents.events import (
    AgentCompleted,
    AgentExecuting,
    AgentFailed,
    AgentInitialized,
    AgentReady,
    AgentShutdown,
    AgentSuspended,
)
from app.runtime.agents.interfaces import BaseAgent, IAgentHooks
from app.runtime.agents.results import AgentResult, AgentStatus

logger = logging.getLogger(__name__)


class AgentState(StrEnum):
    CREATED = "CREATED"
    INITIALIZED = "INITIALIZED"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    SUSPENDED = "SUSPENDED"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"
    TERMINATED = "TERMINATED"


class InvalidStateTransitionError(Exception):
    pass


class AgentLifecycleManager:
    """
    Manages the state transitions for an agent.
    Responsible for broadcasting internal events and triggering hooks.
    """

    def __init__(self, agent: BaseAgent, hooks: list[IAgentHooks], agent_id: str, task_id: str):
        self._agent = agent
        self._hooks = hooks
        self._state = AgentState.CREATED
        self._agent_id = agent_id
        self._task_id = task_id
        self._events_emitted = []  # For testing/telemetry

    @property
    def state(self) -> AgentState:
        return self._state

    def _transition(self, to_state: AgentState, allowed_from: set[AgentState]):
        if self._state not in allowed_from:
            raise InvalidStateTransitionError(f"Cannot transition from {self._state} to {to_state}")
        self._state = to_state

    def _emit(self, event):
        self._events_emitted.append(event)
        # Note: In a real system, we might push this to a dedicated telemetry sink (not EventBus).
        logger.debug(f"Telemetry: {event}")

    def initialize(self, context: AgentContext):
        self._transition(AgentState.INITIALIZED, {AgentState.CREATED})
        for hook in self._hooks:
            hook.before_initialize(self._agent)

        self._agent.initialize(context)

        for hook in self._hooks:
            hook.after_initialize(self._agent)

        self._emit(AgentInitialized(agent_id=self._agent_id, task_id=self._task_id))
        self._transition(AgentState.READY, {AgentState.INITIALIZED})
        self._emit(AgentReady(agent_id=self._agent_id, task_id=self._task_id))

    async def execute(self) -> AgentResult:
        self._transition(AgentState.RUNNING, {AgentState.READY, AgentState.SUSPENDED})

        for hook in self._hooks:
            hook.before_execute(self._agent)

        self._emit(AgentExecuting(agent_id=self._agent_id, task_id=self._task_id))

        try:
            result = await self._agent.execute()

            if result.status == AgentStatus.SUCCESS:
                self._transition(AgentState.COMPLETED, {AgentState.RUNNING})
                self._emit(
                    AgentCompleted(
                        agent_id=self._agent_id, task_id=self._task_id, metrics=result.metrics
                    )
                )
            else:
                self._transition(AgentState.FAILED, {AgentState.RUNNING})
                self._emit(
                    AgentFailed(
                        agent_id=self._agent_id,
                        task_id=self._task_id,
                        error="Execution failed",
                        metrics=result.metrics,
                    )
                )

            for hook in self._hooks:
                hook.after_execute(self._agent, result)

            return result

        except Exception as e:
            self._transition(AgentState.FAILED, {AgentState.RUNNING})
            self._emit(AgentFailed(agent_id=self._agent_id, task_id=self._task_id, error=str(e)))
            for hook in self._hooks:
                hook.after_execute(self._agent, None)
            raise

    def suspend(self, reason: str = ""):
        self._transition(AgentState.SUSPENDED, {AgentState.RUNNING, AgentState.WAITING})
        for hook in self._hooks:
            hook.before_suspend(self._agent)
        self._agent.suspend()
        self._emit(AgentSuspended(agent_id=self._agent_id, task_id=self._task_id, reason=reason))

    def resume(self):
        # We don't transition here since execute() will transition to RUNNING.
        self._agent.resume()
        for hook in self._hooks:
            hook.after_resume(self._agent)

    def shutdown(self):
        self._transition(
            AgentState.TERMINATED,
            {
                AgentState.CREATED,
                AgentState.INITIALIZED,
                AgentState.READY,
                AgentState.COMPLETED,
                AgentState.FAILED,
                AgentState.SUSPENDED,
                AgentState.WAITING,
            },
        )
        for hook in self._hooks:
            hook.before_shutdown(self._agent)

        self._agent.shutdown()

        for hook in self._hooks:
            hook.after_shutdown(self._agent)

        self._emit(AgentShutdown(agent_id=self._agent_id, task_id=self._task_id))
