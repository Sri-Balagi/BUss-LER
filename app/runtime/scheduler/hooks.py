from abc import ABC, abstractmethod

from app.runtime.policies.context import ExecutionDecision, ExecutionPolicyContext
from app.runtime.tasks.models import ITask


class ISchedulerHooks(ABC):
    """
    Lightweight runtime extension points for the Scheduler lifecycle.
    """
    @abstractmethod
    def before_schedule(self, context: ExecutionPolicyContext) -> None:
        pass

    @abstractmethod
    def before_dispatch(self, task: ITask, decision: ExecutionDecision) -> None:
        pass

    @abstractmethod
    def after_dispatch(self, task: ITask) -> None:
        pass

    @abstractmethod
    def before_retry(self, task: ITask, error: Exception, delay_ms: float) -> None:
        pass

    @abstractmethod
    def after_retry(self, task: ITask) -> None:
        pass

    @abstractmethod
    def before_complete(self, task: ITask) -> None:
        pass

    @abstractmethod
    def after_complete(self, task: ITask) -> None:
        pass

class NullSchedulerHooks(ISchedulerHooks):
    """Default empty implementation of hooks."""
    def before_schedule(self, context: ExecutionPolicyContext) -> None: pass
    def before_dispatch(self, task: ITask, decision: ExecutionDecision) -> None: pass
    def after_dispatch(self, task: ITask) -> None: pass
    def before_retry(self, task: ITask, error: Exception, delay_ms: float) -> None: pass
    def after_retry(self, task: ITask) -> None: pass
    def before_complete(self, task: ITask) -> None: pass
    def after_complete(self, task: ITask) -> None: pass
