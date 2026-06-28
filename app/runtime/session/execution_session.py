from app.runtime.interfaces.session import IExecutionSession
from app.runtime.interfaces.identity import IRuntimeIdentity
from app.runtime.interfaces.memory import IWorkingMemory
from app.runtime.interfaces.budget import IExecutionBudget
from app.runtime.interfaces.cancellation import ICancellationToken

class ExecutionSession(IExecutionSession):
    """
    The Process Control Block (PCB) for an execution.
    Acts purely as an immutable container of its core subsystems.
    """
    def __init__(
        self,
        identity: IRuntimeIdentity,
        memory: IWorkingMemory,
        budget: IExecutionBudget,
        cancellation_token: ICancellationToken,
        enterprise_context_version: str = "v1"
    ):
        self._identity = identity
        self._memory = memory
        self._budget = budget
        self._cancellation_token = cancellation_token
        self._enterprise_context_version = enterprise_context_version

    @property
    def identity(self) -> IRuntimeIdentity:
        return self._identity

    @property
    def memory(self) -> IWorkingMemory:
        return self._memory

    @property
    def budget(self) -> IExecutionBudget:
        return self._budget

    @property
    def cancellation_token(self) -> ICancellationToken:
        return self._cancellation_token

    @property
    def enterprise_context_version(self) -> str:
        return self._enterprise_context_version
