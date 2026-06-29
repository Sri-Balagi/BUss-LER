import logging
from app.runtime.capabilities.interfaces import ICapability
from app.runtime.capabilities.context import CapabilityContext
from app.runtime.capabilities.models.request import CapabilityRequest
from app.runtime.capabilities.models.result import CapabilityResult, ExecutionStatus
from app.runtime.capabilities.middleware.pipeline import CapabilityPipeline
from app.runtime.capabilities.middleware.interfaces import IMiddleware

logger = logging.getLogger(__name__)

class CapabilityLifecycleManager:
    """
    Manages lifecycle transitions for a capability.
    """
    def __init__(self, capability: ICapability, middlewares: list[IMiddleware] = None):
        self.capability = capability
        self.pipeline = CapabilityPipeline(middlewares)
        
    async def execute_request(self, request: CapabilityRequest, context: CapabilityContext) -> CapabilityResult:
        
        async def capability_executor(req: CapabilityRequest, ctx: CapabilityContext) -> CapabilityResult:
            try:
                # Initialize
                await self.capability.initialize(ctx)
                
                # Validate
                await self.capability.validate(req)
                
                # Execute
                return await self.capability.execute(req)
            finally:
                # Always Cleanup
                try:
                    await self.capability.cleanup()
                except Exception as e:
                    logger.error(f"Error during capability cleanup: {e}")

        try:
            return await self.pipeline.execute(request, context, capability_executor)
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            return CapabilityResult(
                status=ExecutionStatus.FAILURE,
                outputs={},
                errors=[str(e)],
                execution_time_ms=0,
                execution_trace_id=request.trace_id
            )
