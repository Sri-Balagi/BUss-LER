import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class OpenTelemetryMiddleware(BaseHTTPMiddleware):
    """Middleware for propagating TraceID and SpanID via OpenTelemetry conventions."""
    async def dispatch(self, request: Request, call_next):
        trace_id = request.headers.get("X-B3-TraceId") or str(uuid.uuid4())
        span_id = request.headers.get("X-B3-SpanId") or str(uuid.uuid4())

        request.state.trace_id = trace_id
        request.state.span_id = span_id

        response = await call_next(request)
        response.headers["X-B3-TraceId"] = trace_id
        response.headers["X-B3-SpanId"] = span_id
        return response
