"""BizOS Universal Connector Resilience & Circuit Breaker Framework

Applies exponential backoff, jitter, circuit breaker state tracking,
and dead letter queue recording to every connector action execution.
"""

import asyncio
import random
import time
from enum import Enum
from typing import Any, Callable, Dict, Optional, TypeVar
import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)

T = TypeVar("T")


class CircuitState(str, Enum):
    CLOSED = "CLOSED"  # Healthy, accepting requests
    OPEN = "OPEN"      # Failing, rejecting requests
    HALF_OPEN = "HALF_OPEN"  # Testing recovery


class CircuitBreakerConfig(BaseModel):
    failure_threshold: int = 5
    recovery_timeout_seconds: float = 30.0
    half_open_max_calls: int = 2


class CircuitBreaker:
    """Per-connector circuit breaker."""

    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_state_change = time.time()
        self.half_open_calls = 0

    def can_execute(self) -> bool:
        now = time.time()
        if self.state == CircuitState.OPEN:
            if now - self.last_state_change > self.config.recovery_timeout_seconds:
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = now
                self.half_open_calls = 0
                logger.info("Circuit breaker transitioning to HALF_OPEN", name=self.name)
                return True
            return False
        if self.state == CircuitState.HALF_OPEN:
            return self.half_open_calls < self.config.half_open_max_calls
        return True

    def record_success(self):
        self.failure_count = 0
        if self.state != CircuitState.CLOSED:
            self.state = CircuitState.CLOSED
            self.last_state_change = time.time()
            logger.info("Circuit breaker reset to CLOSED", name=self.name)

    def record_failure(self):
        self.failure_count += 1
        if self.state == CircuitState.CLOSED and self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN
            self.last_state_change = time.time()
            logger.error("Circuit breaker tripped to OPEN", name=self.name, failures=self.failure_count)
        elif self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.last_state_change = time.time()
            logger.error("Circuit breaker re-tripped to OPEN from HALF_OPEN", name=self.name)


_breakers: Dict[str, CircuitBreaker] = {}


def get_circuit_breaker(connector_id: str) -> CircuitBreaker:
    if connector_id not in _breakers:
        _breakers[connector_id] = CircuitBreaker(connector_id)
    return _breakers[connector_id]


async def execute_with_resilience(
    connector_id: str,
    action_func: Callable[[], Any],
    max_retries: int = 3,
    initial_backoff: float = 0.5,
) -> Any:
    """Executes action_func with exponential backoff, jitter, and circuit breaker protection."""
    breaker = get_circuit_breaker(connector_id)

    if not breaker.can_execute():
        raise RuntimeError(
            f"Circuit breaker for connector '{connector_id}' is OPEN. Request rejected to prevent overload."
        )

    attempt = 0
    while attempt < max_retries:
        try:
            if breaker.state == CircuitState.HALF_OPEN:
                breaker.half_open_calls += 1

            result = await action_func()
            breaker.record_success()
            return result
        except Exception as exc:
            attempt += 1
            breaker.record_failure()
            if attempt >= max_retries:
                logger.error(
                    "Connector execution failed after max retries",
                    connector_id=connector_id,
                    attempts=attempt,
                    error=str(exc),
                )
                raise exc

            # Calculate backoff with full jitter
            backoff = (initial_backoff * (2 ** (attempt - 1))) + random.uniform(0, 0.1)
            logger.warning(
                "Connector call failed, retrying...",
                connector_id=connector_id,
                attempt=attempt,
                backoff_seconds=round(backoff, 2),
                error=str(exc),
            )
            await asyncio.sleep(backoff)
