import time
import uuid
from typing import Any

from app.application.applications.trigger.evaluators import ConditionEvaluatorRegistry
from app.application.applications.trigger.evaluators import ConditionEvaluatorRegistry
from app.domain.applications.base import (
    ApplicationResponse,
    IAsynchronousCognitiveApplication,
    ICognitiveOrchestrator,
)
from app.domain.applications.context.models import ApplicationContext
from app.domain.applications.registry.interfaces import IApplicationRegistry
from app.domain.applications.registry.models import ApplicationMetadata
from app.domain.applications.trigger.models import (
    CognitiveTrigger,
    TriggerContext,
    TriggerExecutionResult,
)
from app.domain.applications.worker.interfaces import IJobScheduler, IJobStore
from app.domain.applications.worker.models import JobRecord, JobStatus
from app.domain.intelligence.capability import CapabilityType
from app.domain.intelligence.platform import IIntelligencePlatform
from app.domain.shared.context import ExecutionContext
from app.shared.events.bus import EventBus
from app.shared.events.models import (
    TriggerAcceptedEvent,
    TriggerCompletedEvent,
    TriggerFailedEvent,
    TriggerReceivedEvent,
    TriggerStartedEvent,
)


class CognitiveTriggerEngine(IAsynchronousCognitiveApplication):
    """Event & Condition-based Trigger Engine application using durable background processing."""

    def __init__(
        self,
        platform: IIntelligencePlatform,
        app_registry: IApplicationRegistry,
        store: IJobStore,
        scheduler: IJobScheduler,
        event_bus: EventBus
    ):
        self._platform = platform
        self._app_registry = app_registry
        self._store = store
        self._scheduler = scheduler
        self._event_bus = event_bus
        self._evaluators = ConditionEvaluatorRegistry()
        self._trigger_configs: dict[str, CognitiveTrigger] = {}

    def metadata(self) -> ApplicationMetadata:
        return ApplicationMetadata(
            id="bizos.trigger.v1",
            name="BizOS Cognitive Trigger Engine",
            description="Orchestrates applications based on events, conditions, and schedules.",
            version="1.0.0",
            supported_capabilities=[] # pure orchestrator
        )

    def supported_capabilities(self) -> list[CapabilityType]:
        return []

    async def execute(self, context: ApplicationContext | ExecutionContext) -> ApplicationResponse:
        raise NotImplementedError("CognitiveTriggerEngine uses CQRS.")

    def register_trigger(self, trigger: CognitiveTrigger) -> None:
        self._trigger_configs[trigger.trigger_id] = trigger

    def get_trigger(self, trigger_id: str) -> CognitiveTrigger | None:
        return self._trigger_configs.get(trigger_id)

    async def submit_job(self, context: ApplicationContext | ExecutionContext) -> str:
        if not isinstance(context, TriggerContext):
            raise ValueError("CognitiveTriggerEngine requires a TriggerContext")

        # Extract the cognitive trigger ID from variables
        trigger_id = context.variables.get("trigger_id")
        if not trigger_id:
            raise ValueError("trigger_id missing from TriggerContext variables")

        job_id = str(uuid.uuid4())

        # Publish TriggerReceivedEvent immediately
        self._event_bus.publish(
            TriggerReceivedEvent(
                correlation_id=context.trace_id or job_id,
                trigger_id=trigger_id,
                tenant_id=context.tenant_id,
                trigger_type=context.trigger_type.value
            )
        )

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
            context = TriggerContext(**job.context_data)
            trigger_id = str(context.variables.get("trigger_id") or "")
            trigger = self.get_trigger(trigger_id)

            if not trigger:
                raise ValueError(f"Trigger {trigger_id} not found")

            if not trigger.enabled:
                raise ValueError(f"Trigger {trigger_id} is disabled")

            # 1. Condition Evaluation
            conditions_met = True
            for condition in trigger.conditions:
                evaluator = self._evaluators.resolve(condition.condition_type)
                if not await evaluator.evaluate(condition, context):
                    conditions_met = False
                    break

            if not conditions_met:
                # Silently skip if conditions aren't met, or track as failed/skipped
                job.status = JobStatus.COMPLETED
                job.result = TriggerExecutionResult(
                    trigger_id=trigger_id,
                    success=False,
                    reason="Conditions not met"
                ).model_dump()
                await self._store.update_job(job)
                return

            # 2. Policy Validation
            # ... Policy engine logic would go here, assume pass for now ...

            # 3. Resolve Target Application
            target_app_id = trigger.action.target_app_id
            target_app = self._app_registry.resolve(target_app_id)
            if not target_app:
                raise ValueError(f"Target application {target_app_id} not found in registry")

            self._event_bus.publish(
                TriggerAcceptedEvent(
                    correlation_id=context.trace_id or job_id,
                    trigger_id=trigger_id,
                    tenant_id=context.tenant_id,
                    target_app_id=target_app_id
                )
            )

            # 4. Job Submission / Dispatch
            # Create a new context for the target application
            target_context_data: dict[str, Any] = {
                "user_id": context.user_id,
                "tenant_id": context.tenant_id,
                "trace_id": context.trace_id or job_id,
                "span_id": str(uuid.uuid4()),
                "variables": {
                    "source_trigger_id": trigger_id,
                    **context.variables
                }
            }
            # Merge payload into context data
            target_context_data.update(trigger.action.payload)

            target_context: ApplicationContext
            if target_app_id == "bizos.worker.v1":
                from app.domain.applications.context.models import WorkerContext
                target_context = WorkerContext(
                    workflow_id=str(target_context_data.get("workflow_id") or "wf-1"),
                    task_id=str(target_context_data.get("task_id") or "task-1"),
                    user_id=str(target_context_data.get("user_id") or ""),
                    tenant_id=str(target_context_data.get("tenant_id") or ""),
                    trace_id=str(target_context_data.get("trace_id") or ""),
                    span_id=str(target_context_data.get("span_id") or ""),
                    variables=dict(target_context_data.get("variables") or {})
                )
            elif target_app_id == "bizos.insights.v1":
                from app.domain.applications.insights.models import InsightContext, InsightExecutionRequest, InsightType
                target_context = InsightContext(
                    insight_type=InsightType.ANOMALY,
                    execution_request=InsightExecutionRequest(required_capabilities=[CapabilityType.REASONING]),
                    user_id=str(target_context_data.get("user_id") or ""),
                    tenant_id=str(target_context_data.get("tenant_id") or ""),
                    trace_id=str(target_context_data.get("trace_id") or ""),
                    span_id=str(target_context_data.get("span_id") or ""),
                    variables=dict(target_context_data.get("variables") or {})
                )
            else:
                target_context = ApplicationContext(
                    user_id=str(target_context_data.get("user_id") or ""),
                    tenant_id=str(target_context_data.get("tenant_id") or ""),
                    trace_id=str(target_context_data.get("trace_id") or ""),
                    span_id=str(target_context_data.get("span_id") or ""),
                    variables=dict(target_context_data.get("variables") or {})
                )

            if hasattr(target_app, 'submit_job'):
                target_job_id = await target_app.submit_job(target_context)
            else:
                # If it's a sync application, execute it immediately
                # target_job_id = None
                # result = await target_app.execute(target_context)
                raise ValueError("TriggerEngine currently only dispatches async ICognitiveApplications via submit_job")

            self._event_bus.publish(
                TriggerStartedEvent(
                    correlation_id=context.trace_id or job_id,
                    trigger_id=trigger_id,
                    tenant_id=context.tenant_id,
                    execution_id=target_job_id,
                    target_app_id=target_app_id
                )
            )

            # In a true system, we'd listen for the target app's completion.
            # For orchestration, we just say the trigger execution is completed.
            job.status = JobStatus.COMPLETED
            job.result = TriggerExecutionResult(
                trigger_id=trigger_id,
                target_job_id=target_job_id,
                success=True,
                reason="Dispatched successfully"
            ).model_dump()

            self._event_bus.publish(
                TriggerCompletedEvent(
                    correlation_id=context.trace_id or job_id,
                    trigger_id=trigger_id,
                    tenant_id=context.tenant_id,
                    execution_id=target_job_id,
                    target_app_id=target_app_id
                )
            )

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)

            trigger_id_str = str(context.variables.get("trigger_id") or "unknown") if 'context' in locals() else "unknown"

            self._event_bus.publish(
                TriggerFailedEvent(
                    correlation_id=getattr(context, 'trace_id', job_id) if 'context' in locals() else job_id,
                    trigger_id=trigger_id_str,
                    tenant_id=getattr(context, 'tenant_id', None) if 'context' in locals() else None,
                    reason=str(e)
                )
            )

        job.updated_at = time.time()
        await self._store.update_job(job)

    def health(self) -> bool:
        return True
