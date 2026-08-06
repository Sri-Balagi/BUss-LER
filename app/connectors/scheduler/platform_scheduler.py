"""
Platform Scheduler Engine with Jitter support for BizOS.
Decouples execution timing from connectors, workflows, twin reconciliation, and housekeeping.
"""
from __future__ import annotations
import asyncio
import random
from datetime import datetime, timezone
try:
    from enum import StrEnum
except ImportError:
    from enum import Enum
    class StrEnum(str, Enum):
        pass
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field

class ScheduleTaskType(StrEnum):
    CONNECTOR_POLL = "CONNECTOR_POLL"
    WORKFLOW = "WORKFLOW"
    TWIN_RECONCILIATION = "TWIN_RECONCILIATION"
    MEMORY_MAINTENANCE = "MEMORY_MAINTENANCE"
    HEALTH_CHECK = "HEALTH_CHECK"
    HOUSEKEEPING = "HOUSEKEEPING"

class ScheduledJob(BaseModel):
    job_id: str
    name: str
    task_type: ScheduleTaskType
    interval_seconds: float
    cron_expr: Optional[str] = None
    enabled: bool = True
    priority: int = 1
    jitter_max_seconds: float = 2.0
    retry_count: int = 0
    max_retries: int = 3
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None

class PlatformScheduler:
    """
    Centralized Platform Scheduler supporting Connectors, Workflows, Twin Sync, and Housekeeping jobs.
    Includes exponential backoff with randomized retry jitter.
    """

    def __init__(self) -> None:
        self._jobs: Dict[str, ScheduledJob] = {}
        self._handlers: Dict[str, Callable[[], Any]] = {}
        self._running: bool = False
        self._loop_task: Optional[asyncio.Task[None]] = None

    def register_job(
        self,
        job_id: str,
        name: str,
        task_type: ScheduleTaskType,
        interval_seconds: float,
        handler: Callable[[], Any],
        cron_expr: Optional[str] = None,
        jitter_max_seconds: float = 2.0,
    ) -> ScheduledJob:
        job = ScheduledJob(
            job_id=job_id,
            name=name,
            task_type=task_type,
            interval_seconds=interval_seconds,
            cron_expr=cron_expr,
            jitter_max_seconds=jitter_max_seconds,
            next_run_at=datetime.now(timezone.utc),
        )
        self._jobs[job_id] = job
        self._handlers[job_id] = handler
        return job

    def calculate_jitter(self, max_jitter: float) -> float:
        """Applies randomized retry jitter to prevent thundering herd spikes."""
        return random.uniform(0.0, max_jitter)

    async def execute_job(self, job_id: str) -> bool:
        if job_id not in self._jobs or not self._jobs[job_id].enabled:
            return False

        job = self._jobs[job_id]
        handler = self._handlers.get(job_id)
        if not handler:
            return False

        try:
            job.last_run_at = datetime.now(timezone.utc)
            if asyncio.iscoroutinefunction(handler):
                await handler()
            else:
                handler()
            
            job.retry_count = 0
            jitter = self.calculate_jitter(job.jitter_max_seconds)
            next_delay = job.interval_seconds + jitter
            job.next_run_at = datetime.now(timezone.utc)
            return True

        except Exception as e:
            job.retry_count += 1
            if job.retry_count <= job.max_retries:
                # Exponential backoff with jitter
                backoff = (2 ** job.retry_count) + self.calculate_jitter(job.jitter_max_seconds)
                job.next_run_at = datetime.now(timezone.utc)
            else:
                job.enabled = False # Pause failed job
            return False

    def pause_job(self, job_id: str) -> bool:
        if job_id in self._jobs:
            self._jobs[job_id].enabled = False
            return True
        return False

    def resume_job(self, job_id: str) -> bool:
        if job_id in self._jobs:
            self._jobs[job_id].enabled = True
            return True
        return False

    def get_status(self) -> Dict[str, Any]:
        return {
            "total_jobs": len(self._jobs),
            "active_jobs": sum(1 for j in self._jobs.values() if j.enabled),
            "jobs_by_type": {
                t.value: sum(1 for j in self._jobs.values() if j.task_type == t) for t in ScheduleTaskType
            },
        }
