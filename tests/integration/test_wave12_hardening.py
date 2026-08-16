import asyncio
from typing import Optional
from uuid import UUID, uuid4

import pytest

from app.domain.infrastructure.repositories import IRepository
from app.infrastructure.audit.logger import AuditLogger
from app.infrastructure.config.manager import ConfigurationManager
from app.infrastructure.observability.health import HealthMonitor, HealthStatus
from app.infrastructure.resilience.policies import (
    CircuitBreaker,
    CircuitBreakerState,
    DeadLetterQueue,
    ExecutionPolicy,
    IdempotencyGuard,
    RetryPolicy,
    TimeoutPolicy,
)
from app.infrastructure.security.abstractions import SecurityContext


# Mock repo for test
class MockRepository(IRepository[dict]):
    def __init__(self):
        self.store = {}

    async def create(self, entity: dict) -> dict:
        entity_id = entity.get("id", str(uuid4()))
        entity["id"] = entity_id
        self.store[entity_id] = entity
        return entity

    async def update(self, entity: dict) -> dict:
        self.store[entity["id"]] = entity
        return entity

    async def delete(self, entity_id: UUID | str) -> bool:
        if entity_id in self.store:
            del self.store[entity_id]
            return True
        return False

    async def get_by_id(self, entity_id: UUID | str) -> dict | None:
        return self.store.get(entity_id)

    async def list(self, limit: int = 100, offset: int = 0) -> list[dict]:
        return list(self.store.values())[offset:offset+limit]

@pytest.mark.asyncio
async def test_repository_crud():
    repo = MockRepository()
    item = await repo.create({"name": "test"})
    assert item["id"] is not None
    assert item["name"] == "test"

    fetched = await repo.get_by_id(item["id"])
    assert fetched["name"] == "test"

    item["name"] = "updated"
    await repo.update(item)

    fetched = await repo.get_by_id(item["id"])
    assert fetched["name"] == "updated"

    items = await repo.list()
    assert len(items) == 1

    deleted = await repo.delete(item["id"])
    assert deleted is True
    assert await repo.get_by_id(item["id"]) is None

@pytest.mark.asyncio
async def test_execution_policy():
    policy = ExecutionPolicy(retry=RetryPolicy(max_retries=2, base_delay=0.01), timeout=TimeoutPolicy(timeout_seconds=0.1))

    attempts = 0
    async def failing_func():
        nonlocal attempts
        attempts += 1
        raise ValueError("Fail")

    with pytest.raises(ValueError):
        await policy.execute(failing_func)

    assert attempts == 3  # Initial + 2 retries

@pytest.mark.asyncio
async def test_circuit_breaker():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)

    async def failing_func():
        raise ValueError("Fail")

    # Attempt 1
    with pytest.raises(ValueError):
        await cb.execute(failing_func)
    assert cb.state == CircuitBreakerState.CLOSED

    # Attempt 2
    with pytest.raises(ValueError):
        await cb.execute(failing_func)
    assert cb.state == CircuitBreakerState.OPEN

    # Attempt 3 (Should fail fast)
    with pytest.raises(Exception, match="Circuit Breaker is OPEN"):
        await cb.execute(failing_func)

    # Wait for recovery
    await asyncio.sleep(0.2)

    # Attempt 4 (Half open -> success -> closed)
    async def success_func():
        return "OK"

    res = await cb.execute(success_func)
    assert res == "OK"
    assert cb.state == CircuitBreakerState.CLOSED

def test_idempotency_guard():
    guard = IdempotencyGuard()
    assert guard.is_processed("req-1") is False
    guard.mark_processed("req-1")
    assert guard.is_processed("req-1") is True

def test_dead_letter_queue():
    dlq = DeadLetterQueue()
    dlq.push({"task": "123"}, "Failed after 3 retries")
    assert dlq.count() == 1

def test_configuration_manager():
    config = ConfigurationManager({"app": {"debug": True, "port": 8000}})
    assert config.get("app.debug") is True
    assert config.get("app.port") == 8000
    config.set("app.port", 9090)
    assert config.get("app.port") == 9090
    assert config.get("app.missing", "default") == "default"

def test_health_monitor():
    monitor = HealthMonitor()
    assert monitor.check_liveness() is True
    assert monitor.check_readiness() is True
    monitor.set_service_health("EventBus", HealthStatus.UNHEALTHY)
    assert monitor.check_readiness() is False

def test_security_context():
    ctx = SecurityContext("user1", "tenant1", ["admin"])
    assert ctx.user_id == "user1"
    assert "admin" in ctx.roles

def test_audit_logger(caplog):
    import logging
    caplog.set_level(logging.INFO)
    logger = AuditLogger()
    logger.log("READ", "Memory", "user1", "SUCCESS")
    assert "AUDIT" in caplog.text
    assert "user1" in caplog.text
    assert "user1" in caplog.text
