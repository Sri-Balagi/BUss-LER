from abc import ABC, abstractmethod

from .budget import IExecutionBudget
from .cancellation import ICancellationToken
from .identity import IRuntimeIdentity
from .memory import IWorkingMemory


class IExecutionSession(ABC):
    """
    The Process Control Block (PCB) for an execution.
    """

    @property
    @abstractmethod
    def identity(self) -> IRuntimeIdentity:
        pass

    @property
    @abstractmethod
    def memory(self) -> IWorkingMemory:
        pass

    @property
    @abstractmethod
    def budget(self) -> IExecutionBudget:
        pass

    @property
    @abstractmethod
    def cancellation_token(self) -> ICancellationToken:
        pass

    @property
    @abstractmethod
    def enterprise_context_version(self) -> str:
        pass


class ISessionFactory(ABC):
    @abstractmethod
    def create_session(self, correlation_id: str | None = None) -> IExecutionSession:
        pass
