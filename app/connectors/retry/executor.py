"""Connector retry framework."""
from __future__ import annotations
import asyncio
import logging
import random
from collections.abc import Callable, Awaitable
from enum import StrEnum
from typing import Any, TypeVar
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
T = TypeVar("T")


class FailureType(StrEnum):
    TRANSIENT = "TRANSIENT"      # retry allowed
    PERMANENT = "PERMANENT"      # dead-letter immediately
    RATE_LIMITED = "RATE_LIMITED"  # honor Retry-After


class RetryPolicy(BaseModel):
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential: bool = True
    jitter: bool = True
    retryable_exceptions: list[str] = Field(default_factory=list)

    def compute_delay(self, attempt: int) -> float:
        if self.exponential:
            delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        else:
            delay = self.base_delay
        if self.jitter:
            delay *= (0.5 + random.random() * 0.5)
        return delay


class RetryResult(BaseModel):
    success: bool
    attempts: int
    last_error: str | None = None
    dead_lettered: bool = False


class RetryExecutor:
    """
    Executes async callables with retry policy.

    Usage::

        policy = RetryPolicy(max_retries=5, base_delay=2.0)
        executor = RetryExecutor(policy)
        result = await executor.execute(my_async_fn, arg1, arg2)
    """

    def __init__(self, policy: RetryPolicy | None = None) -> None:
        self._policy = policy or RetryPolicy()

    async def execute(
        self,
        func: Callable[..., Awaitable[T]],
        *args: Any,
        **kwargs: Any,
    ) -> T:
        last_exc: Exception | None = None
        for attempt in range(self._policy.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exc = e
                if attempt >= self._policy.max_retries:
                    break
                delay = self._policy.compute_delay(attempt)
                logger.warning(
                    "RetryExecutor: attempt %d/%d failed error=%s delay=%.2fs",
                    attempt + 1,
                    self._policy.max_retries,
                    e,
                    delay,
                )
                await asyncio.sleep(delay)

        from app.connectors.exceptions.errors import RetryExhaustedError
        raise RetryExhaustedError(
            f"All {self._policy.max_retries} retries exhausted: {last_exc}",
            attempts=self._policy.max_retries,
        )
