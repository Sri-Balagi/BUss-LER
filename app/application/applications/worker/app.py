import uuid
import time
from typing import AsyncIterator, List

from app.domain.applications.base import IAsynchronousCognitiveApplication, ApplicationResponse
from app.domain.applications.context.models import ApplicationContext, WorkerContext
from app.domain.applications.registry.models import ApplicationMetadata
from app.domain.intelligence.capability import CapabilityType
from app.domain.intelligence.platform import IIntelligencePlatform, UnifiedExecutionRequest
from app.domain.applications.worker.interfaces import IJobStore, IJobScheduler
from app.domain.applications.worker.models import JobRecord, JobStatus

class AutonomousWorkerApplication(IAsynchronousCognitiveApplication):
    
    def __init__(self, platform: IIntelligencePlatform, store: IJobStore, scheduler: IJobScheduler):
        self._platform = platform
        self._store = store
        self._scheduler = scheduler

    def metadata(self) -> ApplicationMetadata:
        return ApplicationMetadata(
            id="bizos.worker.v1",
            name="BizOS Autonomous Worker",
            description="Executes long-running agentic goals via durable background processing.",
            version="1.0.0",
            supported_capabilities=[
                CapabilityType.PLANNING,
                CapabilityType.REASONING,
                CapabilityType.AGENT
            ]
        )

    def supported_capabilities(self) -> List[CapabilityType]:
        return self.metadata().supported_capabilities

    async def execute(self, context: ApplicationContext) -> ApplicationResponse:
        raise NotImplementedError("AutonomousWorkerApplication uses CQRS (submit_job/get_job_status). Synchronous execute is disabled.")

    async def submit_job(self, context: ApplicationContext) -> str:
        if not isinstance(context, WorkerContext):
            raise ValueError("AutonomousWorkerApplication requires a WorkerContext")
            
        job_id = str(uuid.uuid4())
        job = JobRecord(
            job_id=job_id,
            app_id=self.metadata().id,
            status=JobStatus.PENDING,
            context_data=context.model_dump()
        )
        
        await self._store.create_job(job)
        await self._scheduler.enqueue(job_id)
        
        return job_id
        
    async def get_job_status(self, job_id: str) -> JobRecord:
        job = await self._store.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        return job
        
    async def _execute_background_job(self, job_id: str) -> None:
        job = await self._store.get_job(job_id)
        if not job:
            return
            
        job.status = JobStatus.RUNNING
        job.updated_at = time.time()
        await self._store.update_job(job)
        
        try:
            context = WorkerContext(**job.context_data)
            
            try:
                tenant_uuid = uuid.UUID(context.tenant_id)
            except (ValueError, TypeError):
                tenant_uuid = None
                
            goal = context.variables.get("goal", "Execute background task")
            
            result = await self._platform.execute_agent_goal(
                agent_id=uuid.uuid4(),
                goal=goal,
                tenant_id=tenant_uuid
            )
            
            job.result = result.output_data
            job.status = JobStatus.COMPLETED if result.success else JobStatus.FAILED
            if not result.success:
                job.error = "; ".join(result.errors)
                
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)
            
        job.updated_at = time.time()
        await self._store.update_job(job)

    def health(self) -> bool:
        return True
