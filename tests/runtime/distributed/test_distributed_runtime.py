"""
Milestone 3: Distributed Runtime — Unit Tests
===============================================
All tests run WITHOUT a live Redis or Celery broker.
Infrastructure calls are mocked using unittest.mock so these tests pass in any CI environment.
"""
from __future__ import annotations

import json
from unittest.mock import MagicMock, PropertyMock, patch
from uuid import UUID, uuid4

import pytest

from app.runtime.distributed.interfaces import (
    IDistributedScheduler,
    IDistributedSystemBus,
    IWorkerNode,
)
from app.runtime.distributed.worker_node import BizOSWorkerNode

# ---------------------------------------------------------------------------
# IDistributedScheduler — interface stub tests (no broker needed)
# ---------------------------------------------------------------------------

class _StubScheduler(IDistributedScheduler):
    """Minimal in-memory stub that validates the interface contract."""

    def __init__(self) -> None:
        self._tasks: dict[str, str] = {}

    def schedule_task(self, task_name: str, payload, queue: str = "default") -> str:
        task_id = str(uuid4())
        self._tasks[task_id] = "PENDING"
        return task_id

    def get_task_status(self, task_id: str) -> str:
        return self._tasks.get(task_id, "UNKNOWN")

    def revoke_task(self, task_id: str, terminate: bool = False) -> None:
        if task_id in self._tasks:
            self._tasks[task_id] = "REVOKED"


def test_distributed_scheduler_schedule_and_status():
    scheduler = _StubScheduler()
    task_id = scheduler.schedule_task("bizos.tasks.run_agent", {"agent_id": "123"})
    assert task_id
    assert scheduler.get_task_status(task_id) == "PENDING"


def test_distributed_scheduler_revoke():
    scheduler = _StubScheduler()
    task_id = scheduler.schedule_task("bizos.tasks.run_workflow", {})
    scheduler.revoke_task(task_id)
    assert scheduler.get_task_status(task_id) == "REVOKED"


# ---------------------------------------------------------------------------
# CeleryDistributedScheduler — mock the Celery class where it is used
# ---------------------------------------------------------------------------

def test_celery_scheduler_schedule_task():
    """Verify schedule_task calls send_task correctly on the Celery app."""
    from app.runtime.distributed import celery_scheduler as mod

    mock_celery_cls = MagicMock()
    mock_celery_app = MagicMock()
    mock_celery_cls.return_value = mock_celery_app

    mock_result = MagicMock()
    mock_result.id = "celery-task-abc-123"
    mock_celery_app.send_task.return_value = mock_result

    with patch.object(mod, "Celery", mock_celery_cls):
        from app.runtime.distributed.celery_scheduler import CeleryDistributedScheduler
        scheduler = CeleryDistributedScheduler(broker_url="redis://localhost:6379/0")
        task_id = scheduler.schedule_task("bizos.tasks.echo", {"msg": "hello"})

    assert task_id == "celery-task-abc-123"
    mock_celery_app.send_task.assert_called_once_with(
        "bizos.tasks.echo",
        kwargs={"msg": "hello"},
        queue="default",
    )


def test_celery_scheduler_get_task_status():
    from app.runtime.distributed import celery_scheduler as mod

    mock_celery_cls = MagicMock()
    mock_celery_app = MagicMock()
    mock_celery_cls.return_value = mock_celery_app

    mock_async_result = MagicMock()
    mock_async_result.state = "SUCCESS"
    mock_celery_app.AsyncResult.return_value = mock_async_result

    with patch.object(mod, "Celery", mock_celery_cls):
        from app.runtime.distributed.celery_scheduler import CeleryDistributedScheduler
        scheduler = CeleryDistributedScheduler(broker_url="redis://localhost:6379/0")
        status = scheduler.get_task_status("some-task-id")

    assert status == "SUCCESS"


def test_celery_scheduler_revoke_task():
    from app.runtime.distributed import celery_scheduler as mod

    mock_celery_cls = MagicMock()
    mock_celery_app = MagicMock()
    mock_celery_cls.return_value = mock_celery_app

    with patch.object(mod, "Celery", mock_celery_cls):
        from app.runtime.distributed.celery_scheduler import CeleryDistributedScheduler
        scheduler = CeleryDistributedScheduler(broker_url="redis://localhost:6379/0")
        scheduler.revoke_task("some-task-id", terminate=True)

    mock_celery_app.control.revoke.assert_called_once_with("some-task-id", terminate=True)


# ---------------------------------------------------------------------------
# IDistributedSystemBus — interface stub tests
# ---------------------------------------------------------------------------

class _StubBus(IDistributedSystemBus):
    def __init__(self) -> None:
        self._published: list[tuple[str, object]] = []
        self._subscriptions: list[str] = []

    def publish(self, channel: str, message) -> None:
        self._published.append((channel, message))

    def subscribe(self, channel: str) -> None:
        self._subscriptions.append(channel)

    def listen(self):
        yield from []


def test_distributed_system_bus_publish_subscribe():
    bus = _StubBus()
    bus.subscribe("events.agent")
    bus.publish("events.agent", {"type": "AGENT_STARTED", "id": "42"})

    assert "events.agent" in bus._subscriptions
    assert bus._published[0] == ("events.agent", {"type": "AGENT_STARTED", "id": "42"})


# ---------------------------------------------------------------------------
# RedisSystemBus — mock the redis module where it is used
# ---------------------------------------------------------------------------

def test_redis_system_bus_publish():
    from app.runtime.distributed import redis_bus as mod

    mock_redis_module = MagicMock()
    mock_client = MagicMock()
    mock_redis_module.Redis.from_url.return_value = mock_client
    mock_client.pubsub.return_value = MagicMock()

    with patch.object(mod, "redis", mock_redis_module):
        from app.runtime.distributed.redis_bus import RedisSystemBus
        bus = RedisSystemBus(redis_url="redis://localhost:6379/0")
        bus.publish("events.agent", {"type": "AGENT_STARTED"})

    mock_client.publish.assert_called_once_with(
        "events.agent", json.dumps({"type": "AGENT_STARTED"})
    )


def test_redis_system_bus_subscribe():
    from app.runtime.distributed import redis_bus as mod

    mock_redis_module = MagicMock()
    mock_client = MagicMock()
    mock_pubsub = MagicMock()
    mock_redis_module.Redis.from_url.return_value = mock_client
    mock_client.pubsub.return_value = mock_pubsub

    with patch.object(mod, "redis", mock_redis_module):
        from app.runtime.distributed.redis_bus import RedisSystemBus
        bus = RedisSystemBus(redis_url="redis://localhost:6379/0")
        bus.subscribe("events.agent")

    mock_pubsub.subscribe.assert_called_once_with("events.agent")


# ---------------------------------------------------------------------------
# BizOSWorkerNode — concrete worker node
# ---------------------------------------------------------------------------

def test_worker_node_defaults():
    node = BizOSWorkerNode()
    assert isinstance(node.node_id, UUID)
    assert node.is_healthy is True
    assert node.last_heartbeat is None


def test_worker_node_heartbeat():
    node = BizOSWorkerNode()
    node.heartbeat()
    assert node.last_heartbeat is not None
    assert node.is_healthy is True


def test_worker_node_mark_unhealthy():
    node = BizOSWorkerNode()
    node.mark_unhealthy()
    assert node.is_healthy is False
    # Heartbeat restores health
    node.heartbeat()
    assert node.is_healthy is True


def test_worker_node_custom_id():
    uid = uuid4()
    node = BizOSWorkerNode(node_id=uid)
    assert node.node_id == uid
