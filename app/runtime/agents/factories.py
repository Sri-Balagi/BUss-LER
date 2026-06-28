from typing import Type
from app.runtime.agents.interfaces import IAgentFactory, BaseAgent
from app.runtime.agents.specification import AgentSpecification

class TransientFactory(IAgentFactory):
    """
    Creates a new instance of an agent for every execution.
    """
    def __init__(self, agent_class: Type[BaseAgent]):
        self._agent_class = agent_class

    def create_agent(self, specification: AgentSpecification) -> BaseAgent:
        return self._agent_class(specification)

    def release_agent(self, agent: BaseAgent) -> None:
        # Transient agents are just garbage collected.
        pass

class SingletonFactory(IAgentFactory):
    """
    Reuses the same agent instance for all executions.
    Useful for stateless workers or workers that manage their own internal connection pools.
    """
    def __init__(self, agent_class: Type[BaseAgent]):
        self._agent_class = agent_class
        self._instance: BaseAgent | None = None

    def create_agent(self, specification: AgentSpecification) -> BaseAgent:
        if self._instance is None:
            self._instance = self._agent_class(specification)
        return self._instance

    def release_agent(self, agent: BaseAgent) -> None:
        # Singleton instance is kept alive.
        pass
