import asyncio
import concurrent.futures
from collections.abc import Callable
from typing import Any

from app.infrastructure.execution.strategy import (
    ExecutionContext,
    ExecutionResult,
    ExecutionStrategy,
    IExecutionStrategy,
)


def _execute_wrapper(callable_fn: Callable[..., Any], args: tuple, kwargs: dict) -> Any:
    """Wrapper to execute the callable inside the subprocess."""
    # This must be a top-level function so it can be pickled
    return callable_fn(*args, **kwargs)


class SubprocessExecutionStrategy(IExecutionStrategy):
    """Executes callables in a separate process for isolation."""

    @property
    def strategy_type(self) -> ExecutionStrategy:
        return ExecutionStrategy.SUBPROCESS

    async def execute(
        self, callable_fn: Callable[..., Any], context: ExecutionContext, *args: Any, **kwargs: Any
    ) -> ExecutionResult:
        loop = asyncio.get_running_loop()

        try:
            # Run in a separate process pool
            with concurrent.futures.ProcessPoolExecutor(max_workers=1) as pool:
                # Use asyncio.wait_for to apply the timeout from context
                future = loop.run_in_executor(pool, _execute_wrapper, callable_fn, args, kwargs)
                result = await asyncio.wait_for(future, timeout=context.timeout_seconds)

            return ExecutionResult(
                success=True,
                result=result,
                lifecycle_id=context.lifecycle_id
            )
        except TimeoutError:
            return ExecutionResult(
                success=False,
                error=f"Execution timed out after {context.timeout_seconds}s",
                lifecycle_id=context.lifecycle_id
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=str(e),
                lifecycle_id=context.lifecycle_id
            )

