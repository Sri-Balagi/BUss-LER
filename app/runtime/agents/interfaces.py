from abc import ABC, abstractmethod
from typing import Any
from app.runtime.agents.specification import AgentSpecification
from app.runtime.agents.context import AgentContext
from app.runtime.agents.results import AgentResult

class IAgentHooks(ABC):
    """
    Passive extension points for tracing and observability.
    Should never modify runtime state.
    """
    @abstractmethod
    def before_initialize(self, agent: 'BaseAgent') -> None:
        pass

    @abstractmethod
    def after_initialize(self, agent: 'BaseAgent') -> None:
        pass

    @abstractmethod
    def before_execute(self, agent: 'BaseAgent') -> None:
        pass

    @abstractmethod
    def after_execute(self, agent: 'BaseAgent', result: AgentResult | None) -> None:
        pass

    @abstractmethod
    def before_suspend(self, agent: 'BaseAgent') -> None:
        pass

    @abstractmethod
    def after_resume(self, agent: 'BaseAgent') -> None:
        pass

    @abstractmethod
    def before_shutdown(self, agent: 'BaseAgent') -> None:
        pass

    @abstractmethod
    def after_shutdown(self, agent: 'BaseAgent') -> None:
        pass

class BaseAgent(ABC):
    """
    The definitive execution contract for a BizOS worker.
    Execution-only sandbox.
    """
    def __init__(self, specification: AgentSpecification):
        self._specification = specification
        self.context: AgentContext | None = None

    @property
    def specification(self) -> AgentSpecification:
        return self._specification

    @abstractmethod
    def initialize(self, context: AgentContext) -> None:
        """Called once before execution begins."""
        pass

    @abstractmethod
    async def execute(self) -> AgentResult:
        """Core execution loop."""
        pass

    @abstractmethod
    def suspend(self) -> None:
        """Called when the agent is being suspended (e.g., waiting for external input)."""
        pass

    @abstractmethod
    def resume(self) -> None:
        """Called when the agent resumes execution after suspension."""
        pass

    @abstractmethod
    def cancel(self) -> None:
        """Called to abort execution."""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Called for final cleanup before destruction."""
        pass

class IAgentFactory(ABC):
    """
    Controls instantiation and lifecycle pooling for agents.
    """
    @abstractmethod
    def create_agent(self, specification: AgentSpecification) -> BaseAgent:
        pass

    @abstractmethod
    def release_agent(self, agent: BaseAgent) -> None:
        pass
