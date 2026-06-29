from typing import List, Optional
from app.runtime.capabilities.models.request import CapabilityRequest
from app.runtime.capabilities.models.result import CapabilityResult, ExecutionStatus
from app.runtime.capabilities.models.resolution import CapabilityResolutionContext
from app.runtime.capabilities.context import CapabilityContext
from app.runtime.capabilities.registry import CapabilityRegistry
from app.runtime.capabilities.middleware.interfaces import IMiddleware
from app.runtime.capabilities.lifecycle import CapabilityLifecycleManager
from app.runtime.capabilities.executor import ICapabilityExecutor
import logging
import time

logger = logging.getLogger(__name__)

class CapabilityManager(ICapabilityExecutor):
    def __init__(self, registry: CapabilityRegistry, middlewares: List[IMiddleware] = None):
        self.registry = registry
        self.middlewares = middlewares or []
        
    async def execute_capability(
        self, 
        request: CapabilityRequest, 
        context: Optional[CapabilityContext] = None
    ) -> CapabilityResult:
        
        start_time = time.time()
        context = context or CapabilityContext()
        
        # 1. Map CapabilityRequest to CapabilityResolutionContext
        resolution_context = CapabilityResolutionContext(
            capability_id=request.capability_id,
            operation=request.operation,
            requested_version=request.execution_metadata.get("version"),
            execution_trace_id=request.trace_id,
            permissions=request.permissions,
            caller_agent_id=request.caller_id
        )
        
        # 2. Resolve via Registry
        try:
            decision = self.registry.resolve(resolution_context)
        except Exception as e:
            logger.error(f"Failed to resolve capability: {e}")
            return CapabilityResult(
                status=ExecutionStatus.FAILURE,
                outputs={},
                errors=[f"Resolution failure: {e}"],
                execution_time_ms=int((time.time() - start_time) * 1000),
                execution_trace_id=request.trace_id
            )
            
        # 3. Instantiate Capability via Factory
        try:
            capability = decision.selected_factory.create(decision.selected_specification)
        except Exception as e:
            logger.error(f"Failed to create capability: {e}")
            return CapabilityResult(
                status=ExecutionStatus.FAILURE,
                outputs={},
                errors=[f"Factory failure: {e}"],
                execution_time_ms=int((time.time() - start_time) * 1000),
                execution_trace_id=request.trace_id
            )
            
        # 4. Execute via LifecycleManager (which invokes the Middleware Pipeline)
        lifecycle_manager = CapabilityLifecycleManager(capability, self.middlewares)
        
        return await lifecycle_manager.execute_request(request, context)
