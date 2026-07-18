import asyncio
from app.domain.applications.registry.interfaces import IApplicationRegistry
from app.domain.applications.worker.interfaces import IJobScheduler, IJobStore
from app.domain.applications.worker.models import JobStatus

class LocalJobScheduler(IJobScheduler):
    def __init__(self, store: IJobStore, registry: IApplicationRegistry):
        self._store = store
        self._registry = registry

    async def enqueue(self, job_id: str) -> None:
        asyncio.create_task(self._process_job(job_id))
        
    async def _process_job(self, job_id: str) -> None:
        job = await self._store.get_job(job_id)
        if not job:
            return
            
        app = self._registry.resolve(job.app_id)
        if not app or not hasattr(app, '_execute_background_job'):
            # Mark failed
            job.status = JobStatus.FAILED
            job.error = "Application not found or does not support background execution"
            await self._store.update_job(job)
            return
            
        await app._execute_background_job(job_id)
