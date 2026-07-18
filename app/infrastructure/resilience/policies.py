from typing import Callable, Any
from enum import Enum
import asyncio
import time

class CircuitBreakerState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class RetryPolicy:
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, exponential: bool = True):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.exponential = exponential

class TimeoutPolicy:
    def __init__(self, timeout_seconds: float = 30.0):
        self.timeout_seconds = timeout_seconds

class ExecutionPolicy:
    def __init__(self, retry: RetryPolicy = None, timeout: TimeoutPolicy = None):
        self.retry = retry or RetryPolicy()
        self.timeout = timeout or TimeoutPolicy()

    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        attempts = 0
        last_exception = None
        
        while attempts <= self.retry.max_retries:
            try:
                if self.timeout.timeout_seconds > 0:
                    return await asyncio.wait_for(func(*args, **kwargs), timeout=self.timeout.timeout_seconds)
                else:
                    return await func(*args, **kwargs)
            except Exception as e:
                attempts += 1
                last_exception = e
                if attempts > self.retry.max_retries:
                    break
                delay = self.retry.base_delay * (2 ** (attempts - 1)) if self.retry.exponential else self.retry.base_delay
                await asyncio.sleep(delay)
                
        raise last_exception

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self.state = CircuitBreakerState.CLOSED
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0

    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        if self.state == CircuitBreakerState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise Exception("Circuit Breaker is OPEN")
                
        try:
            result = await func(*args, **kwargs)
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitBreakerState.OPEN
            raise e

class IdempotencyGuard:
    def __init__(self):
        self._processed_keys = set()
        
    def is_processed(self, key: str) -> bool:
        return key in self._processed_keys
        
    def mark_processed(self, key: str):
        self._processed_keys.add(key)

class DeadLetterQueue:
    def __init__(self):
        self._queue = []
        
    def push(self, item: Any, reason: str):
        self._queue.append({"item": item, "reason": reason, "timestamp": time.time()})
        
    def count(self) -> int:
        return len(self._queue)
