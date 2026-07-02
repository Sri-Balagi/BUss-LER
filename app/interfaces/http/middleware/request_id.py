"""Request ID and Correlation ID middleware.

Injects X-Request-ID and X-Correlation-ID headers into every request/response.
These IDs are propagated through all structured log entries.
"""

from __future__ import annotations

import uuid

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware that injects a unique request ID and correlation ID.

    - X-Request-ID: unique ID per request (generated if not present).
    - X-Correlation-ID: propagated from caller if present, else same as request ID.
    """

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[override]
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        correlation_id = request.headers.get("X-Correlation-ID") or request_id

        # Store on request state for downstream access
        request.state.request_id = request_id
        request.state.correlation_id = correlation_id

        # Bind to structlog context for this request
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            correlation_id=correlation_id,
        )

        try:
            response = await call_next(request)
        finally:
            structlog.contextvars.clear_contextvars()

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Correlation-ID"] = correlation_id
        return response
