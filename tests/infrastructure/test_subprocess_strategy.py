import asyncio

import pytest

from app.infrastructure.execution.strategy import ExecutionContext
from app.infrastructure.execution.subprocess_strategy import SubprocessExecutionStrategy


def sample_function(x, y, *, z=0):
    return x + y + z


def sample_blocking_function():
    import time
    time.sleep(2)
    return "done"


def sample_failing_function():
    raise ValueError("intentional error")


@pytest.mark.asyncio
async def test_subprocess_success():
    strategy = SubprocessExecutionStrategy()
    context = ExecutionContext(timeout_seconds=5.0)

    result = await strategy.execute(sample_function, context, 1, 2, z=3)

    assert result.success is True
    assert result.result == 6
    assert result.error is None


@pytest.mark.asyncio
async def test_subprocess_timeout():
    strategy = SubprocessExecutionStrategy()
    context = ExecutionContext(timeout_seconds=0.5)

    result = await strategy.execute(sample_blocking_function, context)

    assert result.success is False
    assert "timed out" in result.error


@pytest.mark.asyncio
async def test_subprocess_exception():
    strategy = SubprocessExecutionStrategy()
    context = ExecutionContext(timeout_seconds=5.0)

    result = await strategy.execute(sample_failing_function, context)

    assert result.success is False
    assert "intentional error" in result.error
