import threading
from typing import Dict, Optional

from app.domain.applications.worker.models import JobRecord
from app.domain.applications.worker.interfaces import IJobStore

class InMemoryJobStore(IJobStore):
    """In-memory implementation of IJobStore for local execution."""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._jobs: Dict[str, JobRecord] = {}
        
    async def create_job(self, job: JobRecord) -> None:
        with self._lock:
            self._jobs[job.job_id] = job
            
    async def update_job(self, job: JobRecord) -> None:
        with self._lock:
            self._jobs[job.job_id] = job
            
    async def get_job(self, job_id: str) -> Optional[JobRecord]:
        with self._lock:
            return self._jobs.get(job_id)
