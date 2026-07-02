import asyncio

import pytest

from app.infrastructure.execution.factory import ExecutionStrategyFactory
from app.infrastructure.execution.in_process import InProcessExecutionStrategy
from app.infrastructure.execution.strategy import (
    ExecutionContext,
    ExecutionStrategy,
)
from app.infrastructure.execution.subprocess_strategy import (
    SubprocessExecutionStrategy,
)


@pytest.mark.asyncio
async def test_in_process_async_callable():
    strategy = InProcessExecutionStrategy()
    context = ExecutionContext(lifecycle_id="test-123", timeout_seconds=1.0)

    async def my_async_fn(x: int, y: int) -> int:
        return x + y

    result = await strategy.execute(my_async_fn, context, 2, 3)
    assert result.success is True
    assert result.result == 5
    assert result.lifecycle_id == "test-123"


@pytest.mark.asyncio
async def test_in_process_sync_callable():
    strategy = InProcessExecutionStrategy()
    context = ExecutionContext(lifecycle_id="test-456", timeout_seconds=1.0)

    def my_sync_fn(x: int, y: int) -> int:
        return x * y

    result = await strategy.execute(my_sync_fn, context, 4, 5)
    assert result.success is True
    assert result.result == 20
    assert result.lifecycle_id == "test-456"


@pytest.mark.asyncio
async def test_in_process_timeout():
    strategy = InProcessExecutionStrategy()
    context = ExecutionContext(timeout_seconds=0.1)

    async def slow_fn() -> str:
        await asyncio.sleep(0.5)
        return "done"

    result = await strategy.execute(slow_fn, context)
    assert result.success is False
    assert result.error == "timed out"


@pytest.mark.asyncio
async def test_in_process_exception_isolation():
    strategy = InProcessExecutionStrategy()
    context = ExecutionContext()

    def failing_fn() -> None:
        raise ValueError("Something went wrong")

    result = await strategy.execute(failing_fn, context)
    assert result.success is False
    assert result.error is not None
    assert "Something went wrong" in result.error


@pytest.mark.asyncio
async def test_subprocess_execution_raises():
    strategy = SubprocessExecutionStrategy()
    context = ExecutionContext()

    async def dummy() -> None:
        pass

    with pytest.raises(NotImplementedError, match="Wave 2"):
        await strategy.execute(dummy, context)


def test_factory_returns_correct_strategy():
    in_process = ExecutionStrategyFactory.get_strategy(ExecutionStrategy.IN_PROCESS)
    assert isinstance(in_process, InProcessExecutionStrategy)

    subprocess = ExecutionStrategyFactory.get_strategy(ExecutionStrategy.SUBPROCESS)
    assert isinstance(subprocess, SubprocessExecutionStrategy)

    with pytest.raises(NotImplementedError):
        ExecutionStrategyFactory.get_strategy(ExecutionStrategy.CONTAINER)
