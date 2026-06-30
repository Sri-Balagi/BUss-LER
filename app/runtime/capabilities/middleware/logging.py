import logging

from app.runtime.capabilities.context import CapabilityContext
from app.runtime.capabilities.middleware.context import MiddlewareContext
from app.runtime.capabilities.middleware.decision import MiddlewareDecision
from app.runtime.capabilities.middleware.interfaces import IMiddleware
from app.runtime.capabilities.models.request import CapabilityRequest
from app.runtime.capabilities.models.result import CapabilityResult

logger = logging.getLogger(__name__)

class LoggingMiddleware(IMiddleware):
    async def before_execution(
        self, request: CapabilityRequest, cap_context: CapabilityContext, mw_context: MiddlewareContext
    ) -> MiddlewareDecision:
        logger.info(f"Capability executing: {request.capability_id} | Operation: {request.operation}")
        return MiddlewareDecision.ALLOW

    async def after_execution(
        self, request: CapabilityRequest, cap_context: CapabilityContext, mw_context: MiddlewareContext, result: CapabilityResult
    ) -> CapabilityResult:
        logger.info(f"Capability completed: {request.capability_id} | Status: {result.status}")
        return result

    async def on_exception(
        self, request: CapabilityRequest, cap_context: CapabilityContext, mw_context: MiddlewareContext, exception: Exception
    ) -> MiddlewareDecision:
        logger.error(f"Capability failed: {request.capability_id} | Error: {exception}")
        return MiddlewareDecision.ALLOW
