import time
import uuid

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware that manages end-to-end tracing and contextual state.

    Injects:
    - Request ID
    - Correlation ID
    - Trace ID
    - Tenant ID (if resolved)
    - User ID (if resolved)
    - Session ID (if resolved)
    - Request Start Time

    These are attached to `request.state` and bound to the structured logger context.
    """

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore
        start_time = time.time()

        # 1. Resolve IDs from headers or generate new ones
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        correlation_id = request.headers.get("X-Correlation-ID") or request_id
        trace_id = request.headers.get("X-Trace-ID") or str(uuid.uuid4())

        tenant_id = request.headers.get("X-Tenant-ID")
        user_id = request.headers.get("X-User-ID")
        session_id = request.headers.get("X-Session-ID")

        # 2. Attach to request state
        request.state.request_id = request_id
        request.state.correlation_id = correlation_id
        request.state.trace_id = trace_id
        request.state.start_time = start_time

        request.state.tenant_id = tenant_id
        request.state.user_id = user_id
        request.state.session_id = session_id

        # 3. Bind to structlog context
        context_vars = {
            "request_id": request_id,
            "correlation_id": correlation_id,
            "trace_id": trace_id,
        }
        if tenant_id:
            context_vars["tenant_id"] = tenant_id
        if user_id:
            context_vars["user_id"] = user_id
        if session_id:
            context_vars["session_id"] = session_id

        structlog.contextvars.bind_contextvars(**context_vars)

        try:
            response = await call_next(request)
        finally:
            structlog.contextvars.clear_contextvars()

        # 4. Inject tracing headers into response
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Trace-ID"] = trace_id

        return response
