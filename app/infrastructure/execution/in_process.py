import asyncio
import inspect
from collections.abc import Callable
from typing import Any

from app.infrastructure.execution.strategy import (
    ExecutionContext,
    ExecutionResult,
    ExecutionStrategy,
    IExecutionStrategy,
)


class InProcessExecutionStrategy(IExecutionStrategy):
    """Executes callables within the current process event loop or thread pool."""

    @property
    def strategy_type(self) -> ExecutionStrategy:
        return ExecutionStrategy.IN_PROCESS

    async def execute(
        self, callable_fn: Callable[..., Any], context: ExecutionContext, *args: Any, **kwargs: Any
    ) -> ExecutionResult:
        try:
            if inspect.iscoroutinefunction(callable_fn):
                coro = callable_fn(*args, **kwargs)
                result = await asyncio.wait_for(coro, timeout=context.timeout_seconds)
            else:
                loop = asyncio.get_running_loop()

                # Run sync functions in the default executor (thread pool)
                def run_sync() -> Any:
                    return callable_fn(*args, **kwargs)

                future = loop.run_in_executor(None, run_sync)
                result = await asyncio.wait_for(future, timeout=context.timeout_seconds)

            return ExecutionResult(success=True, result=result, lifecycle_id=context.lifecycle_id)

        except TimeoutError:
            return ExecutionResult(
                success=False, error="timed out", lifecycle_id=context.lifecycle_id
            )
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), lifecycle_id=context.lifecycle_id)
