from abc import ABC, abstractmethod


class BizOSAgent(ABC):
    """
    Base class for defining an Agent using the SDK.
    Agents encapsulate capabilities, LLM integration, and state.
    """

    @abstractmethod
    def get_capabilities(self) -> list[str]:
        """Returns the capabilities provided by this agent."""
        pass

    @abstractmethod
    def execute(self, task: str, **kwargs) -> str:
        """Executes a task."""
        pass
