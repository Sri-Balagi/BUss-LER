from app.runtime.capabilities.context import CapabilityContext
from app.runtime.capabilities.middleware.context import MiddlewareContext
from app.runtime.capabilities.middleware.decision import MiddlewareDecision
from app.runtime.capabilities.middleware.interfaces import IMiddleware
from app.runtime.capabilities.models.request import CapabilityRequest
from app.runtime.capabilities.models.result import CapabilityResult


class PolicyMiddleware(IMiddleware):
    async def before_execution(
        self, request: CapabilityRequest, cap_context: CapabilityContext, mw_context: MiddlewareContext
    ) -> MiddlewareDecision:
        mw_context.policy_decisions["timeout_enforced"] = request.timeout_ms or 30000
        return MiddlewareDecision.ALLOW

    async def after_execution(
        self, request: CapabilityRequest, cap_context: CapabilityContext, mw_context: MiddlewareContext, result: CapabilityResult
    ) -> CapabilityResult:
        return result

    async def on_exception(
        self, request: CapabilityRequest, cap_context: CapabilityContext, mw_context: MiddlewareContext, exception: Exception
    ) -> MiddlewareDecision:
        if "retry_eligible" in mw_context.metadata:
            return MiddlewareDecision.RETRY
        return MiddlewareDecision.ALLOW
