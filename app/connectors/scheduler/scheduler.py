"""Generic Connector Scheduler."""
from __future__ import annotations
import asyncio
import logging
import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Callable, Awaitable
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class TaskType(StrEnum):
    SYNC = "sync"
    TOKEN_REFRESH = "token_refresh"
    WEBHOOK_RENEWAL = "webhook_renewal"
    HEALTH_CHECK = "health_check"
    CLEANUP = "cleanup"
    HEARTBEAT = "heartbeat"
    MAINTENANCE = "maintenance"
    CUSTOM = "custom"


class ScheduledTask(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    connector_id: str
    profile_id: str = "default"
    task_type: TaskType
    interval_seconds: int
    description: str = ""
    enabled: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_run_at: datetime | None = None
    next_run_at: datetime | None = None
    run_count: int = 0
    failure_count: int = 0


class ConnectorScheduler:
    """
    Generic scheduler for all connector periodic operations.

    Supports: sync, token refresh, webhook renewal, health checks,
    cleanup, heartbeat, and custom operations.
    """

    def __init__(self) -> None:
        self._tasks: dict[str, ScheduledTask] = {}
        self._handlers: dict[str, Callable[..., Awaitable[Any]]] = {}
        self._asyncio_tasks: dict[str, asyncio.Task[None]] = {}

    def schedule(
        self,
        task: ScheduledTask,
        handler: Callable[..., Awaitable[Any]],
    ) -> str:
        """Schedule a task with its async handler function."""
        self._tasks[task.task_id] = task
        self._handlers[task.task_id] = handler
        self._asyncio_tasks[task.task_id] = asyncio.create_task(
            self._run_loop(task.task_id)
        )
        logger.info(
            "Scheduled task %s[%s] type=%s interval=%ds",
            task.connector_id,
            task.task_id,
            task.task_type.value,
            task.interval_seconds,
        )
        return task.task_id

    def cancel(self, task_id: str) -> None:
        t = self._asyncio_tasks.pop(task_id, None)
        if t and not t.done():
            t.cancel()
        self._tasks.pop(task_id, None)
        self._handlers.pop(task_id, None)

    def list_tasks(self, connector_id: str | None = None) -> list[ScheduledTask]:
        tasks = list(self._tasks.values())
        if connector_id:
            tasks = [t for t in tasks if t.connector_id == connector_id]
        return tasks

    async def shutdown(self) -> None:
        for task_id in list(self._asyncio_tasks):
            self.cancel(task_id)

    async def _run_loop(self, task_id: str) -> None:
        while True:
            task = self._tasks.get(task_id)
            handler = self._handlers.get(task_id)
            if task is None or handler is None or not task.enabled:
                break
            await asyncio.sleep(task.interval_seconds)
            try:
                await handler()
                task.last_run_at = datetime.now(UTC)
                task.run_count += 1
                logger.debug("Scheduled task %s executed", task_id)
            except Exception as e:
                task.failure_count += 1
                logger.error("Scheduled task %s failed: %s", task_id, e)
