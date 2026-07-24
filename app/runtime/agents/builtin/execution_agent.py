import asyncio
import uuid

import structlog

from app.runtime.agents.context import AgentContext
from app.runtime.agents.interfaces import BaseAgent, IAgentFactory
from app.runtime.agents.results import AgentResult, AgentResultStatus
from app.runtime.agents.specification import AgentSpecification

logger = structlog.get_logger(__name__)


class ExecutionAgent(BaseAgent):
    """Built-in agent for handling capability execution (e.g., executing plans)."""

    def initialize(self, context: AgentContext) -> None:
        self.context = context
        logger.debug("ExecutionAgent initialized", identity=self.specification.identity)

    async def execute(self) -> AgentResult:
        logger.info("ExecutionAgent executing capability", identity=self.specification.identity)

        # M9 Stub execution
        await asyncio.sleep(0.1)

        return AgentResult(
            status=AgentResultStatus.SUCCESS,
            output={"execution_status": "Step executed successfully"},
            metrics={"duration_ms": 100},
            artifacts=[]
        )

    def suspend(self) -> None:
        pass

    def resume(self) -> None:
        pass

    def cancel(self) -> None:
        pass

    def shutdown(self) -> None:
        pass


class ExecutionAgentFactory(IAgentFactory):
    def create_agent(self, specification: AgentSpecification) -> BaseAgent:
        return ExecutionAgent(specification)

    def release_agent(self, agent: BaseAgent) -> None:
        pass


def get_execution_agent_spec() -> AgentSpecification:
    return AgentSpecification(
        identity=f"builtin-execution-{uuid.uuid4()}",
        capabilities=["execute_action", "apply_change"],
        permissions=[],
    )
