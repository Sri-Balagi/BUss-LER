import uuid

from app.runtime.capabilities.context import CapabilityContext
from app.runtime.capabilities.middleware.context import MiddlewareContext
from app.runtime.capabilities.middleware.decision import MiddlewareDecision
from app.runtime.capabilities.middleware.interfaces import IMiddleware
from app.runtime.capabilities.models.request import CapabilityRequest
from app.runtime.capabilities.models.result import CapabilityResult


class TracingMiddleware(IMiddleware):
    async def before_execution(
        self, request: CapabilityRequest, cap_context: CapabilityContext, mw_context: MiddlewareContext
    ) -> MiddlewareDecision:
        trace_id = request.trace_id or uuid.uuid4()
        mw_context.trace_data["trace_id"] = trace_id
        mw_context.trace_data["span_id"] = uuid.uuid4()
        return MiddlewareDecision.ALLOW

    async def after_execution(
        self, request: CapabilityRequest, cap_context: CapabilityContext, mw_context: MiddlewareContext, result: CapabilityResult
    ) -> CapabilityResult:
        result.execution_trace_id = mw_context.trace_data.get("trace_id")
        return result

    async def on_exception(
        self, request: CapabilityRequest, cap_context: CapabilityContext, mw_context: MiddlewareContext, exception: Exception
    ) -> MiddlewareDecision:
        return MiddlewareDecision.ALLOW
