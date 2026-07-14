"""
Celery-backed distributed task scheduler for BizOS.

Design notes
------------
- Celery is imported at module level. The package is a required dependency
  for distributed mode (installed via `uv add celery[redis]`).
- The Celery app is configured lazily on first construction so tests can
  mock the class before any instance is created.
"""
from __future__ import annotations

import os
from typing import Any

from celery import Celery  # type: ignore[import]

from app.runtime.distributed.interfaces import IDistributedScheduler


class CeleryDistributedScheduler(IDistributedScheduler):
    """
    Concrete distributed scheduler backed by Celery + Redis.

    The broker URL is resolved from the environment variable
    ``CELERY_BROKER_URL`` (defaults to ``redis://localhost:6379/0``).
    """

    def __init__(self, broker_url: str | None = None) -> None:
        self._broker_url: str = broker_url or os.getenv(
            "CELERY_BROKER_URL", "redis://localhost:6379/0"
        )
        self._result_backend: str = os.getenv(
            "CELERY_RESULT_BACKEND", self._broker_url
        )
        self._app: Celery = Celery(
            "bizos",
            broker=self._broker_url,
            backend=self._result_backend,
        )
        self._app.conf.task_serializer = "json"
        self._app.conf.result_serializer = "json"
        self._app.conf.accept_content = ["json"]
        self._app.conf.timezone = "UTC"

    @property
    def celery_app(self) -> Celery:
        return self._app

    def schedule_task(self, task_name: str, payload: Any, queue: str = "default") -> str:
        """Send a task to the Celery queue and return the task_id."""
        result = self._app.send_task(task_name, kwargs=payload, queue=queue)
        return result.id

    def get_task_status(self, task_id: str) -> str:
        """Query Celery for the current state of a task."""
        result = self._app.AsyncResult(task_id)
        return result.state  # PENDING | STARTED | SUCCESS | FAILURE | RETRY

    def revoke_task(self, task_id: str, terminate: bool = False) -> None:
        """Revoke (cancel) a pending or running Celery task."""
        self._app.control.revoke(task_id, terminate=terminate)
