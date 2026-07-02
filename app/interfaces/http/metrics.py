"""Prometheus metrics for BizOS.

Exposes HTTP request metrics, runtime execution counters, and exception counts.
Metrics are collected passively and exposed at /metrics for Prometheus scraping.

NOTE: In production, /metrics should only be accessible on internal networks.
"""

from __future__ import annotations

import time

from fastapi import Request, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)
from starlette.middleware.base import BaseHTTPMiddleware

# ── HTTP Metrics ──────────────────────────────────────────────────────────────
HTTP_REQUESTS_TOTAL = Counter(
    "bizos_http_requests_total",
    "Total number of HTTP requests",
    ["method", "path", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "bizos_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

# ── Runtime Metrics ───────────────────────────────────────────────────────────
RUNTIME_EXECUTIONS_TOTAL = Counter(
    "bizos_runtime_executions_total",
    "Total number of runtime task executions",
    ["status"],
)

COGNITIVE_SESSIONS_TOTAL = Counter(
    "bizos_cognitive_sessions_total",
    "Total number of cognitive (intelligence) sessions started",
)

# ── Error Metrics ─────────────────────────────────────────────────────────────
EXCEPTIONS_TOTAL = Counter(
    "bizos_exceptions_total",
    "Total number of unhandled exceptions",
    ["exception_type"],
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware that records HTTP metrics for every request."""

    # Paths to exclude from metrics collection
    EXCLUDE_PATHS = {"/metrics", "/api/v1/health", "/api/v1/live", "/api/v1/ready"}

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[override]
        if request.url.path in self.EXCLUDE_PATHS:
            return await call_next(request)

        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start

        # Normalize path to avoid high cardinality
        path = request.url.path

        HTTP_REQUESTS_TOTAL.labels(
            method=request.method,
            path=path,
            status_code=str(response.status_code),
        ).inc()

        HTTP_REQUEST_DURATION_SECONDS.labels(
            method=request.method,
            path=path,
        ).observe(duration)

        return response


def metrics_endpoint(request: Request) -> Response:
    """Prometheus /metrics endpoint handler."""
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
