from collections.abc import Awaitable, Callable
from typing import Any

from app.domain.intelligence.context import IntelligenceContext
from app.domain.intelligence.execution import IExecutionPolicy
from app.domain.intelligence.pipeline import IIntelligencePipeline, PipelineContext, PipelineResult
from app.shared.events.bus import EventBus
from app.shared.events.models import DomainEvent


class PipelineManager:
    """Coordinates execution pipelines without inventing custom orchestration."""

    async def run_pipeline(self, pipeline: Any, context: PipelineContext[Any]) -> PipelineResult[Any]:
        # In a real system, this might log entry/exit, handle top-level retries, etc.
        return await pipeline.execute(context)


class EventRouter:
    """Publishes intelligence domain events to the EventBus."""

    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus

    async def publish(self, event: DomainEvent) -> None:
        self._event_bus.publish(event)


class ExecutionCoordinator:
    """Manages parallel execution, timeouts, and applies execution policies."""

    async def execute_with_policy(
        self,
        policy: IExecutionPolicy,
        context: IntelligenceContext,
        task: Callable[[], Awaitable[Any]]
    ) -> Any:
        # Pass control to the specific execution policy.
        # This centralizes where timeouts and cancellation tokens would be injected.
        return await policy.execute(context, task)


class IntelligenceKernel:
    """
    The runtime backbone for every intelligence subsystem.
    Exposes managers and coordinators to standardize execution.
    """

    def __init__(self, event_bus: EventBus):
        self.pipeline_manager = PipelineManager()
        self.event_router = EventRouter(event_bus)
        self.execution_coordinator = ExecutionCoordinator()

    # Additional ContextManager and TelemetryManager logic would go here.
