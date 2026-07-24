import threading

from app.domain.applications.worker.interfaces import IJobStore
from app.domain.applications.worker.models import JobRecord


class InMemoryJobStore(IJobStore):
    """In-memory implementation of IJobStore for local execution."""

    def __init__(self):
        self._lock = threading.Lock()
        self._jobs: dict[str, JobRecord] = {}

    async def create_job(self, job: JobRecord) -> None:
        with self._lock:
            self._jobs[job.job_id] = job

    async def update_job(self, job: JobRecord) -> None:
        with self._lock:
            self._jobs[job.job_id] = job

    async def get_job(self, job_id: str) -> JobRecord | None:
        with self._lock:
            return self._jobs.get(job_id)
