from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Type

from app.domain.intelligence.context import IntelligenceContext
from app.domain.intelligence.telemetry import IntelligenceMetrics


class UnifiedExecutionRequest(BaseModel):
    request_type: str  # e.g., "reasoning", "planning", "agent_goal", "workflow_optimization"
    tenant_id: Optional[UUID] = None
    agent_id: Optional[UUID] = None
    input_data: Dict[str, Any]
    correlation_id: str


class UnifiedExecutionMetrics(IntelligenceMetrics):
    total_latency_ms: float = 0.0
    capabilities_invoked: List[str] = Field(default_factory=list)


class UnifiedExecutionResult(IntelligenceContext):
    success: bool
    output_data: Dict[str, Any]
    metrics: UnifiedExecutionMetrics
    errors: List[str] = Field(default_factory=list)
    
    class Config:
        frozen = True


class IIntelligencePlatform(ABC):
    """Unified Facade for all Wave 5 Intelligence capabilities."""

    @abstractmethod
    async def execute_request(self, request: UnifiedExecutionRequest) -> UnifiedExecutionResult:
        """Execute a generic intelligence request by composing necessary pipelines."""
        pass
        
    @abstractmethod
    async def execute_agent_goal(self, agent_id: UUID, goal: str, tenant_id: Optional[UUID] = None) -> UnifiedExecutionResult:
        """Start an Agent Cognitive Loop for a specific goal."""
        pass
        
    @abstractmethod
    async def optimize_workflow(self, workflow_id: UUID, tenant_id: Optional[UUID] = None) -> UnifiedExecutionResult:
        """Manually trigger a Workflow Optimization."""
        pass
        
    @abstractmethod
    async def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Retrieve execution status and metrics."""
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema: Type[BaseModel],
        tools: Optional[List[Any]] = None,
        model: Optional[str] = None
    ) -> BaseModel:
        pass
        
    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Any]] = None,
        model: Optional[str] = None
    ) -> str:
        pass
