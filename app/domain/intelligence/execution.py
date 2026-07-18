import abc
from typing import Awaitable, Callable, Any

from app.domain.intelligence.context import IntelligenceContext


class IExecutionPolicy(abc.ABC):
    """
    Base interface for reusable execution coordination policies
    applied by the Intelligence Kernel.
    """
    
    @abc.abstractmethod
    async def execute(self, context: IntelligenceContext, task: Callable[[], Awaitable[Any]]) -> Any:
        """Executes the provided async task under the strict semantics of this policy."""
        pass


class SequentialExecution(IExecutionPolicy):
    """Executes precisely in the order invoked without parallelism."""
    
    async def execute(self, context: IntelligenceContext, task: Callable[[], Awaitable[Any]]) -> Any:
        return await task()


class RetryExecution(IExecutionPolicy):
    """Applies exponential backoff for transient provider failures."""
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        
    async def execute(self, context: IntelligenceContext, task: Callable[[], Awaitable[Any]]) -> Any:
        # In a real implementation, we would catch specific transient exceptions and asyncio.sleep
        return await task()


class ParallelExecution(IExecutionPolicy):
    """Spins up asynchronous execution branches safely bounded by tenant limits."""
    
    async def execute(self, context: IntelligenceContext, task: Callable[[], Awaitable[Any]]) -> Any:
        # Dummy wrapper for now. Actual implementation requires task lists rather than a single task.
        return await task()
