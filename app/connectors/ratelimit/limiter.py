"""Rate limiting framework for the connector platform."""
from __future__ import annotations
import asyncio
import logging
import time
from collections import deque
from enum import StrEnum
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class RateLimitStrategy(StrEnum):
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    ADAPTIVE = "adaptive"


class QuotaStatus(BaseModel):
    remaining: int
    limit: int
    reset_at: float | None = None
    exhausted: bool = False


class TokenBucket:
    """Token bucket rate limiter. Thread-safe with asyncio."""

    def __init__(self, capacity: int, refill_rate: float) -> None:
        self._capacity = capacity
        self._tokens = float(capacity)
        self._refill_rate = refill_rate  # tokens per second
        self._last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: int = 1) -> None:
        async with self._lock:
            await self._refill()
            while self._tokens < tokens:
                wait = (tokens - self._tokens) / self._refill_rate
                logger.debug("TokenBucket: waiting %.2fs for %d tokens", wait, tokens)
                await asyncio.sleep(wait)
                await self._refill()
            self._tokens -= tokens

    async def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self._capacity, self._tokens + elapsed * self._refill_rate)
        self._last_refill = now

    def quota_status(self) -> QuotaStatus:
        return QuotaStatus(
            remaining=int(self._tokens),
            limit=self._capacity,
        )


class SlidingWindowLimiter:
    """Sliding window rate limiter."""

    def __init__(self, max_calls: int, window_seconds: float) -> None:
        self._max_calls = max_calls
        self._window = window_seconds
        self._calls: deque[float] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: int = 1) -> None:
        async with self._lock:
            now = time.monotonic()
            # Remove expired entries
            while self._calls and self._calls[0] < now - self._window:
                self._calls.popleft()

            if len(self._calls) + tokens > self._max_calls:
                oldest = self._calls[0] if self._calls else now
                wait = oldest + self._window - now
                if wait > 0:
                    logger.debug("SlidingWindow: waiting %.2fs", wait)
                    await asyncio.sleep(wait)

            for _ in range(tokens):
                self._calls.append(time.monotonic())

    def quota_status(self) -> QuotaStatus:
        now = time.monotonic()
        active = sum(1 for t in self._calls if t >= now - self._window)
        return QuotaStatus(
            remaining=max(0, self._max_calls - active),
            limit=self._max_calls,
        )


class RateLimiter:
    """
    Unified rate limiter — wraps a strategy (TokenBucket or SlidingWindow).

    Usage::

        limiter = RateLimiter.token_bucket(capacity=5000, refill_rate=1.39)
        await limiter.acquire()
    """

    def __init__(self, backend: TokenBucket | SlidingWindowLimiter) -> None:
        self._backend = backend

    @classmethod
    def token_bucket(cls, capacity: int, refill_rate: float) -> "RateLimiter":
        return cls(TokenBucket(capacity=capacity, refill_rate=refill_rate))

    @classmethod
    def sliding_window(cls, max_calls: int, window_seconds: float) -> "RateLimiter":
        return cls(SlidingWindowLimiter(max_calls=max_calls, window_seconds=window_seconds))

    async def acquire(self, tokens: int = 1) -> None:
        await self._backend.acquire(tokens)

    async def handle_retry_after(self, retry_after: int) -> None:
        logger.info("RateLimiter: honoring Retry-After=%ds", retry_after)
        await asyncio.sleep(retry_after)

    def quota_status(self) -> QuotaStatus:
        return self._backend.quota_status()
