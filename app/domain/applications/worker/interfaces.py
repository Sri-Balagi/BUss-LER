import abc

from app.domain.applications.worker.models import JobRecord


class IJobStore(abc.ABC):
    """Durable store for job states."""

    @abc.abstractmethod
    async def create_job(self, job: JobRecord) -> None:
        pass

    @abc.abstractmethod
    async def update_job(self, job: JobRecord) -> None:
        pass

    @abc.abstractmethod
    async def get_job(self, job_id: str) -> JobRecord | None:
        pass

class IJobScheduler(abc.ABC):
    """Abstract scheduler for durable asynchronous execution."""

    @abc.abstractmethod
    async def enqueue(self, job_id: str) -> None:
        """Enqueue a job for background execution."""
        pass
