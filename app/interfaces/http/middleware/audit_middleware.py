import time
import uuid

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.bootstrap.container import get_container
from app.domain.security.interfaces import IAuditPublisher
from app.shared.events.models import AuditCategory, AuditEvent

logger = structlog.get_logger(__name__)


def get_audit_publisher(request: Request) -> IAuditPublisher:
    """
    Helper to encapsulate access to the IAuditPublisher dependency.
    This prevents the middleware from being tightly coupled to FastAPI's request.app.state
    or global singletons directly.
    """
    try:
        return get_container().resolve(IAuditPublisher)
    except Exception as e:
        logger.error("audit_publisher_resolution_failed", error=str(e))
        # Return a no-op publisher if DI fails so business ops don't fail
        class NoOpPublisher(IAuditPublisher):
            def publish_audit(self, event: AuditEvent) -> None:
                pass
        return NoOpPublisher()


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware that captures all incoming API requests and publishes an AuditEvent.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Generate a request ID if one doesn't exist
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        correlation_id = getattr(request.state, "correlation_id", request.headers.get("X-Correlation-ID", request_id))

        start_time = time.perf_counter()

        try:
            response = await call_next(request)
            result_status = "SUCCESS" if 200 <= response.status_code < 400 else "FAILURE"
            status_code = response.status_code
        except Exception:
            result_status = "ERROR"
            status_code = 500
            raise
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Extract basic request info
            path = request.url.path
            method = request.method

            # Avoid auditing high-frequency health probes
            if path not in {"/api/v1/health", "/api/v1/live", "/metrics"}:
                publisher = get_audit_publisher(request)

                event = AuditEvent(
                    correlation_id=correlation_id,
                    trace_id=request_id,
                    category=AuditCategory.API_REQUEST,
                    action=method,
                    resource=path,
                    result=result_status,
                    metadata={
                        "status_code": status_code,
                        "duration_ms": duration_ms,
                        "client_ip": request.client.host if request.client else None,
                        "user_agent": request.headers.get("user-agent")
                    }
                )
                publisher.publish_audit(event)

        return response
