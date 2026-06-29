import time
from typing import List, Callable, Awaitable
from app.runtime.capabilities.models.request import CapabilityRequest
from app.runtime.capabilities.models.result import CapabilityResult, ExecutionStatus
from app.runtime.capabilities.context import CapabilityContext
from app.runtime.capabilities.middleware.context import MiddlewareContext
from app.runtime.capabilities.middleware.interfaces import IMiddleware
from app.runtime.capabilities.middleware.decision import MiddlewareDecision
import logging

logger = logging.getLogger(__name__)

class CapabilityPipeline:
    """
    Manages the sequential execution of middlewares wrapping the capability execution.
    """
    def __init__(self, middlewares: List[IMiddleware] = None):
        self.middlewares = middlewares or []
        
    def add_middleware(self, middleware: IMiddleware) -> None:
        self.middlewares.append(middleware)
        
    async def execute(
        self, 
        request: CapabilityRequest, 
        cap_context: CapabilityContext,
        capability_executor: Callable[[CapabilityRequest, CapabilityContext], Awaitable[CapabilityResult]]
    ) -> CapabilityResult:
        
        mw_context = MiddlewareContext()
        
        # 1. Before Execution
        for mw in self.middlewares:
            decision = await mw.before_execution(request, cap_context, mw_context)
            if decision == MiddlewareDecision.DENY:
                return CapabilityResult(
                    status=ExecutionStatus.FAILURE,
                    outputs={},
                    errors=["Execution denied by middleware: " + mw.__class__.__name__],
                    execution_time_ms=int(time.time() * 1000) - mw_context.start_time_ms,
                    execution_trace_id=request.trace_id,
                    validation_results=mw_context.metrics
                )
            elif decision == MiddlewareDecision.SHORT_CIRCUIT:
                # Assume middleware set some specific result in context
                if "short_circuit_result" in mw_context.metadata:
                    return mw_context.metadata["short_circuit_result"]
                return CapabilityResult(
                    status=ExecutionStatus.SUCCESS,
                    outputs={},
                    warnings=["Execution short-circuited by middleware: " + mw.__class__.__name__],
                    execution_time_ms=int(time.time() * 1000) - mw_context.start_time_ms,
                    execution_trace_id=request.trace_id
                )
            elif decision == MiddlewareDecision.RETRY:
                pass
                
        # 2. Execute BaseCapability
        try:
            result = await capability_executor(request, cap_context)
        except Exception as e:
            # 3. On Exception
            for mw in reversed(self.middlewares):
                await mw.on_exception(request, cap_context, mw_context, e)
                
            return CapabilityResult(
                status=ExecutionStatus.FAILURE,
                outputs={},
                errors=[str(e)],
                execution_time_ms=int(time.time() * 1000) - mw_context.start_time_ms,
                execution_trace_id=request.trace_id
            )
            
        # 4. After Execution
        for mw in reversed(self.middlewares):
            result = await mw.after_execution(request, cap_context, mw_context, result)
            
        # Enrich result with middleware context metrics
        result.validation_results.update(mw_context.metrics)
        result.warnings.extend(mw_context.warnings)
        
        return result
