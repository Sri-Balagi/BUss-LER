from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.intelligence.context import IntelligenceContext
from app.domain.intelligence.telemetry import IntelligenceMetrics


class UnifiedExecutionRequest(BaseModel):
    request_type: str  # e.g., "reasoning", "planning", "agent_goal", "workflow_optimization"
    tenant_id: UUID | None = None
    agent_id: UUID | None = None
    input_data: dict[str, Any]
    correlation_id: str


class UnifiedExecutionMetrics(IntelligenceMetrics):
    correlation_id: str = ""
    total_latency_ms: float = 0.0
    capabilities_invoked: list[str] = Field(default_factory=list)


class UnifiedExecutionResult(IntelligenceContext):
    success: bool
    output_data: dict[str, Any]
    metrics: UnifiedExecutionMetrics
    errors: list[str] = Field(default_factory=list)

    class Config:
        frozen = True


class IIntelligencePlatform(ABC):
    """Unified Facade for all Wave 5 Intelligence capabilities."""

    @abstractmethod
    async def execute_request(self, request: UnifiedExecutionRequest) -> UnifiedExecutionResult:
        """Execute a generic intelligence request by composing necessary pipelines."""
        pass

    @abstractmethod
    async def execute_agent_goal(self, agent_id: UUID, goal: str, tenant_id: UUID | None = None) -> UnifiedExecutionResult:
        """Start an Agent Cognitive Loop for a specific goal."""
        pass

    @abstractmethod
    async def optimize_workflow(self, workflow_id: UUID, tenant_id: UUID | None = None) -> UnifiedExecutionResult:
        """Manually trigger a Workflow Optimization."""
        pass

    @abstractmethod
    async def get_execution_status(self, execution_id: str) -> dict[str, Any]:
        """Retrieve execution status and metrics."""
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema: type[BaseModel],
        tools: list[Any] | None = None,
        model: str | None = None
    ) -> BaseModel:
        pass

    @abstractmethod
    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        tools: list[Any] | None = None,
        model: str | None = None
    ) -> str:
        pass

    @abstractmethod
    async def generate_embeddings(self, text: str, model: str | None = None) -> list[float]:
        pass
