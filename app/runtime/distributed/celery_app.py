"""
Celery application entry point for BizOS worker processes.

Usage
-----
Start a worker with::

    celery -A app.runtime.distributed.celery_app worker --loglevel=info

The worker will auto-discover tasks registered under the ``app.runtime.workers``
package (to be implemented in Milestone 4+).
"""
from __future__ import annotations

import os

try:
    from celery import Celery

    _broker = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    _backend = os.getenv("CELERY_RESULT_BACKEND", _broker)

    app = Celery(
        "bizos",
        broker=_broker,
        backend=_backend,
    )

    app.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="UTC",
        enable_utc=True,
        worker_prefetch_multiplier=1,
        task_acks_late=True,  # Ensures at-least-once delivery
    )

    from celery.signals import worker_process_init

    @worker_process_init.connect
    def init_worker(**kwargs):
        """Initialize the DI container once per worker process."""
        from app.bootstrap.container import _global_container, build_container
        if _global_container is None:
            build_container()

except ImportError:
    # Graceful degradation: app is None when celery is not installed.
    # Tests that test distributed behaviour directly should mock or skip.
    app = None
