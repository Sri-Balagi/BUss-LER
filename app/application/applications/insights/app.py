import time
import uuid

from app.domain.applications.base import ApplicationResponse, IAsynchronousCognitiveApplication
from app.domain.applications.context.models import ApplicationContext
from app.domain.applications.insights.models import InsightContext, InsightGenerated, InsightReport
from app.domain.applications.registry.models import ApplicationMetadata
from app.domain.applications.worker.interfaces import IJobScheduler, IJobStore
from app.domain.applications.worker.models import JobRecord, JobStatus
from app.domain.intelligence.capability import CapabilityType
from app.domain.intelligence.platform import IIntelligencePlatform, UnifiedExecutionRequest
from app.domain.shared.context import ExecutionContext
from app.shared.events.bus import EventBus


class InsightsGenerationApplication(IAsynchronousCognitiveApplication):

    def __init__(self, platform: IIntelligencePlatform, store: IJobStore, scheduler: IJobScheduler, event_bus: EventBus):
        self._platform = platform
        self._store = store
        self._scheduler = scheduler
        self._event_bus = event_bus

    def metadata(self) -> ApplicationMetadata:
        return ApplicationMetadata(
            id="bizos.insights.v1",
            name="BizOS Insights Engine",
            description="Generates proactive insights, anomaly reports, and strategic foresight.",
            version="1.0.0",
            supported_capabilities=[
                CapabilityType.TWIN,
                CapabilityType.RETRIEVAL,
                CapabilityType.REASONING
            ]
        )

    def supported_capabilities(self) -> list[CapabilityType]:
        return self.metadata().supported_capabilities

    async def execute(self, context: ApplicationContext | ExecutionContext) -> ApplicationResponse:
        raise NotImplementedError("InsightsGenerationApplication uses CQRS (submit_job/get_job_status). Synchronous execute is disabled.")

    async def submit_job(self, context: ApplicationContext | ExecutionContext) -> str:
        if not isinstance(context, InsightContext):
            raise ValueError("InsightsGenerationApplication requires an InsightContext")

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
            context = InsightContext(**job.context_data)

            # Since tenant_id is string we can just use it directly, or convert it for the platform if needed.
            # Platform `tenant_id` is typed as Optional[UUID] typically, let's attempt to convert it if it's a valid UUID, otherwise None.
            try:
                tenant_uuid = uuid.UUID(context.tenant_id) if getattr(context, 'tenant_id', None) else None
            except (ValueError, TypeError):
                tenant_uuid = None

            # Build UnifiedExecutionRequest
            exec_req = UnifiedExecutionRequest(
                request_type="insight_generation",
                tenant_id=tenant_uuid,
                input_data={
                    "required_capabilities": context.execution_request.required_capabilities,
                    "parameters": context.execution_request.parameters
                },
                correlation_id=context.trace_id or str(uuid.uuid4())
            )

            result = await self._platform.execute_request(exec_req)

            if result.success:
                # Construct canonical InsightReport
                report = InsightReport(
                    report_id=str(uuid.uuid4()),
                    tenant_id=context.tenant_id,
                    insight_type=context.insight_type,
                    title=result.output_data.get("title", f"{context.insight_type.value} Report"),
                    summary=result.output_data.get("summary", ""),
                    findings=result.output_data.get("findings", []),
                    recommendations=result.output_data.get("recommendations", []),
                    confidence=result.output_data.get("confidence", 1.0),
                    supporting_evidence=result.output_data.get("supporting_evidence", {}),
                    execution_metadata={
                        "job_id": job_id,
                        "latency_ms": 0.0 # Could extract from metrics
                    }
                )

                job.result = report.model_dump()
                job.status = JobStatus.COMPLETED

                # Publish event
                event = InsightGenerated(
                    report_id=report.report_id,
                    tenant_id=context.tenant_id,
                    insight_type=context.insight_type,
                    execution_id=job_id,
                    correlation_id=context.trace_id or str(uuid.uuid4())
                )
                self._event_bus.publish(event)
            else:
                job.status = JobStatus.FAILED
                job.error = "; ".join(result.errors)

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)

        job.updated_at = time.time()
        await self._store.update_job(job)

    def health(self) -> bool:
        return True
