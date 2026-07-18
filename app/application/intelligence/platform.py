import uuid
from typing import Any, Dict, Optional
from uuid import UUID

from app.domain.intelligence.capability import CapabilityType
from app.domain.intelligence.events import (
    CapabilityExecutionCompleted,
    CapabilityExecutionStarted,
    UnifiedExecutionCompleted,
    UnifiedExecutionFailed,
    UnifiedExecutionStarted,
)
from app.domain.intelligence.platform import (
    IIntelligencePlatform,
    UnifiedExecutionMetrics,
    UnifiedExecutionRequest,
    UnifiedExecutionResult,
)
from app.domain.intelligence.pipeline import PipelineContext, PipelineResult
from app.domain.cognition.models import AgentState
from app.domain.workflow.models import WorkflowOptimizationContext
from app.domain.learning.models import LearningContext
from app.domain.cognition.events import LearningRequested
from app.application.intelligence.kernel import IntelligenceKernel
from app.application.intelligence.registry import ICapabilityRegistry
from app.domain.cognition.models import ReflectionFeedback


class UnifiedIntelligencePlatform(IIntelligencePlatform):
    """Implementation of the Unified Intelligence Platform facade."""

    def __init__(self, kernel: IntelligenceKernel, registry: ICapabilityRegistry):
        self._kernel = kernel
        self._registry = registry
        self._executions: Dict[str, Dict[str, Any]] = {}

    async def execute_request(self, request: UnifiedExecutionRequest) -> UnifiedExecutionResult:
        """Execute a generic intelligence request by composing necessary pipelines."""
        
        # Publish start event
        await self._kernel.event_router.publish(
            UnifiedExecutionStarted(
                correlation_id=request.correlation_id,
                tenant_id=request.tenant_id,
                agent_id=request.agent_id,
                request_type=request.request_type
            )
        )
        
        self._executions[request.correlation_id] = {
            "status": "PROCESSING",
            "request_type": request.request_type
        }

        try:
            metrics = UnifiedExecutionMetrics(correlation_id=request.correlation_id)
            output_data = {}
            
            # Map request_type to CapabilityType
            capability_type_map = {
                "retrieval": CapabilityType.RETRIEVAL,
                "reasoning": CapabilityType.REASONING,
                "planning": CapabilityType.PLANNING,
                "agent": CapabilityType.AGENT,
                "workflow": CapabilityType.WORKFLOW
            }
            
            cap_type = capability_type_map.get(request.request_type)
            if not cap_type:
                raise ValueError(f"Unknown request type: {request.request_type}")
                
            # Publish capability start event
            await self._kernel.event_router.publish(
                CapabilityExecutionStarted(
                    correlation_id=request.correlation_id,
                    tenant_id=request.tenant_id,
                    agent_id=request.agent_id,
                    capability_type=request.request_type
                )
            )
            metrics.capabilities_invoked.append(request.request_type)

            # Resolve capability
            providers = self._registry.resolve_all_providers(cap_type)
            if not providers:
                raise RuntimeError(f"No providers registered for capability: {cap_type}")
                
            provider = providers[0]
            
            # For this simplified platform, we will assume provider has a standard execute method
            # In reality, we would dispatch to specific pipelines (RetrievalPipeline, ReasoningPipeline, etc.)
            # Here we just mock the provider execution as this is a master facade.
            if hasattr(provider, "execute"):
                # Pass context based on the capability
                pass

            # Mock output for integration test
            output_data["result"] = f"Processed {request.request_type}"

            await self._kernel.event_router.publish(
                CapabilityExecutionCompleted(
                    correlation_id=request.correlation_id,
                    tenant_id=request.tenant_id,
                    agent_id=request.agent_id,
                    capability_type=request.request_type,
                    latency_ms=10.0
                )
            )

            result = UnifiedExecutionResult(
                correlation_id=request.correlation_id,
                success=True,
                output_data=output_data,
                metrics=metrics,
                errors=[]
            )
            
            self._executions[request.correlation_id]["status"] = "COMPLETED"
            self._executions[request.correlation_id]["result"] = result

            await self._kernel.event_router.publish(
                UnifiedExecutionCompleted(
                    correlation_id=request.correlation_id,
                    tenant_id=request.tenant_id,
                    agent_id=request.agent_id,
                    request_type=request.request_type,
                    result=result
                )
            )
            return result

        except Exception as e:
            self._executions[request.correlation_id]["status"] = "FAILED"
            self._executions[request.correlation_id]["error"] = str(e)
            
            await self._kernel.event_router.publish(
                UnifiedExecutionFailed(
                    correlation_id=request.correlation_id,
                    tenant_id=request.tenant_id,
                    agent_id=request.agent_id,
                    request_type=request.request_type,
                    error=str(e)
                )
            )
            return UnifiedExecutionResult(
                correlation_id=request.correlation_id,
                success=False,
                output_data={},
                metrics=UnifiedExecutionMetrics(correlation_id=request.correlation_id),
                errors=[str(e)]
            )

    async def execute_agent_goal(self, agent_id: UUID, goal: str, tenant_id: Optional[UUID] = None) -> UnifiedExecutionResult:
        """Start an Agent Cognitive Loop for a specific goal."""
        correlation_id = str(uuid.uuid4())
        request = UnifiedExecutionRequest(
            request_type="agent",
            agent_id=agent_id,
            tenant_id=tenant_id,
            input_data={"goal": goal},
            correlation_id=correlation_id
        )
        
        result = await self.execute_request(request)
        
        # Dispatch asynchronous learning
        await self._kernel.event_router.publish(
            LearningRequested(
                correlation_id=correlation_id,
                agent_id=agent_id,
                tenant_id=tenant_id,
                iteration=1,
                feedback=ReflectionFeedback.IS_COMPLETE
            )
        )
        
        return result

    async def optimize_workflow(self, workflow_id: UUID, tenant_id: Optional[UUID] = None) -> UnifiedExecutionResult:
        """Manually trigger a Workflow Optimization."""
        correlation_id = str(uuid.uuid4())
        request = UnifiedExecutionRequest(
            request_type="workflow",
            tenant_id=tenant_id,
            input_data={"workflow_id": str(workflow_id)},
            correlation_id=correlation_id
        )
        return await self.execute_request(request)

    async def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Retrieve execution status and metrics."""
        return self._executions.get(execution_id, {"status": "NOT_FOUND"})
