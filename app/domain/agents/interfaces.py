from abc import ABC, abstractmethod

from app.domain.agents.models import Agent, AgentTemplate
from app.shared.enums import AgentType, AgentCapability


class IAgentRegistry(ABC):
    @abstractmethod
    def register_agent(self, agent: Agent) -> None:
        pass

    @abstractmethod
    def get_agent(self, agent_id: str) -> Agent | None:
        pass

    @abstractmethod
    def list_agents(self) -> list[Agent]:
        pass

    @abstractmethod
    def find_by_type(self, agent_type: AgentType) -> list[Agent]:
        pass

    @abstractmethod
    def find_by_capability(self, capability: AgentCapability) -> list[Agent]:
        pass

class IAgentRuntime(ABC):
    """
    High-level orchestrator interface for Agent operations.
    Designed to sit above the Intelligence Kernel and coordinate
    multi-agent execution, goals, and workflows.
    """
    @abstractmethod
    async def spawn_agent(self, name: str, template: AgentTemplate | None = None, capabilities: list[AgentCapability] | None = None) -> Agent:
        pass

    @abstractmethod
    async def execute_goal(self, agent_id: str, goal_description: str) -> dict:
        pass

    @abstractmethod
    async def get_agent_state(self, agent_id: str) -> dict:
        pass

    @abstractmethod
    async def delegate_task(self, from_agent_id: str, to_agent_id: str, task_description: str) -> dict:
        pass
