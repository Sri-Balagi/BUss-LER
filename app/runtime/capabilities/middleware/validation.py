from app.runtime.capabilities.context import CapabilityContext
from app.runtime.capabilities.middleware.context import MiddlewareContext
from app.runtime.capabilities.middleware.decision import MiddlewareDecision
from app.runtime.capabilities.middleware.interfaces import IMiddleware
from app.runtime.capabilities.models.request import CapabilityRequest
from app.runtime.capabilities.models.result import CapabilityResult


class ValidationMiddleware(IMiddleware):
    async def before_execution(
        self, request: CapabilityRequest, cap_context: CapabilityContext, mw_context: MiddlewareContext
    ) -> MiddlewareDecision:
        if not request.caller_id:
            mw_context.metrics["validation_error"] = "Missing caller_id"
            return MiddlewareDecision.DENY

        return MiddlewareDecision.ALLOW

    async def after_execution(
        self, request: CapabilityRequest, cap_context: CapabilityContext, mw_context: MiddlewareContext, result: CapabilityResult
    ) -> CapabilityResult:
        return result

    async def on_exception(
        self, request: CapabilityRequest, cap_context: CapabilityContext, mw_context: MiddlewareContext, exception: Exception
    ) -> MiddlewareDecision:
        return MiddlewareDecision.ALLOW
