from collections.abc import Callable
from typing import Any

from app.infrastructure.execution.strategy import (
    ExecutionContext,
    ExecutionResult,
    ExecutionStrategy,
    IExecutionStrategy,
)


class SubprocessExecutionStrategy(IExecutionStrategy):
    """Executes callables in a separate process for isolation."""

    @property
    def strategy_type(self) -> ExecutionStrategy:
        return ExecutionStrategy.SUBPROCESS

    async def execute(
        self, callable_fn: Callable[..., Any], context: ExecutionContext, *args: Any, **kwargs: Any
    ) -> ExecutionResult:
        raise NotImplementedError("Wave 2")
