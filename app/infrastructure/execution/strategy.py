from abc import ABC, abstractmethod
from collections.abc import Callable
from enum import StrEnum
from typing import Any

from pydantic import BaseModel


class ExecutionStrategy(StrEnum):
    """Supported execution strategies for tools/operations."""

    IN_PROCESS = "in_process"
    SUBPROCESS = "subprocess"
    SANDBOXED = "sandboxed"
    CONTAINER = "container"
    REMOTE_WORKER = "remote_worker"


class ExecutionContext(BaseModel):
    """Context passed to the execution strategy."""

    lifecycle_id: str | None = None
    timeout_seconds: float = 30.0
    sandbox_policy: Any | None = None  # To avoid circular dependency with domain, we use Any here. In practice, it's a SandboxPolicy.


class ExecutionResult(BaseModel):
    """Result of an execution strategy invocation."""

    success: bool
    result: Any | None = None
    error: str | None = None
    lifecycle_id: str | None = None


class IExecutionStrategy(ABC):
    """Abstract interface for execution strategies."""

    @property
    @abstractmethod
    def strategy_type(self) -> ExecutionStrategy:
        """Return the type of this execution strategy."""
        pass

    @abstractmethod
    async def execute(
        self, callable_fn: Callable[..., Any], context: ExecutionContext, *args: Any, **kwargs: Any
    ) -> ExecutionResult:
        """
        Execute the callable with the given arguments within the specified context.
        Must not raise exceptions from the callable; instead, return success=False.
        """
        pass
