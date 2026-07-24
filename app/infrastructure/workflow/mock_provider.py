from copy import deepcopy

from app.domain.intelligence.capability import CapabilityMetadata, CapabilityType
from app.domain.intelligence.provider import ProviderLifecycleStatus
from app.domain.workflow.models import (
    IWorkflowIntelligenceProvider,
    WorkflowOptimizationContext,
    WorkflowOptimizationMetrics,
    WorkflowOptimizationResult,
)


class MockWorkflowIntelligenceProvider(IWorkflowIntelligenceProvider):
    """Mock implementation of the Workflow Intelligence Provider for testing."""

    def __init__(self, priority: int = 1, name: str = "MockWorkflowOptimizer"):
        self._priority = priority
        self._name = name
        self._status = ProviderLifecycleStatus.READY

    def get_metadata(self) -> CapabilityMetadata:
        return CapabilityMetadata(
            capability_id=f"workflow-{self._name.lower()}",
            capability_type=CapabilityType.WORKFLOW,
            provider_name=self._name,
            provider_version="1.0.0",
            priority=self._priority,
            supported_features=["mock_optimization"]
        )

    def set_status(self, status: ProviderLifecycleStatus) -> None:
        self._status = status

    def get_status(self) -> ProviderLifecycleStatus:
        return self._status

    async def optimize(self, context: WorkflowOptimizationContext) -> WorkflowOptimizationResult:
        # Simulate optimization: deep copy and just count the tasks
        optimized_workflow = deepcopy(context.workflow)
        task_count = len(optimized_workflow.tasks)

        # Add a dummy optimization note
        context.optimization_suggestions.append("Mock optimization complete")

        metrics = WorkflowOptimizationMetrics(
            optimization_time_ms=10.0,
            tasks_optimized_count=task_count
        )

        return WorkflowOptimizationResult(
            success=True,
            optimized_workflow=optimized_workflow,
            metrics=metrics
        )
