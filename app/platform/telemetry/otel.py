"""OpenTelemetry tracing setup for BizOS.

Tracing is DISABLED by default (OTEL_ENABLED=false).
When enabled, it emits traces to a console exporter or OTLP endpoint.

Zero behavior change when disabled — all functions are no-ops if tracing is off.
"""

from __future__ import annotations

import os
from typing import Any

import structlog

logger = structlog.get_logger()

_tracing_enabled: bool = False


def is_tracing_enabled() -> bool:
    """Check if OpenTelemetry tracing is currently enabled."""
    return _tracing_enabled


def setup_tracing(service_name: str = "bizos", version: str = "6.0.0") -> bool:
    """Initialize OpenTelemetry tracing if OTEL_ENABLED=true.

    Returns True if tracing was successfully initialized, False otherwise.
    This function is safe to call regardless of whether opentelemetry is installed.
    """
    global _tracing_enabled  # noqa: PLW0603

    enabled = os.getenv("OTEL_ENABLED", "false").lower() == "true"
    if not enabled:
        logger.info("OpenTelemetry tracing disabled (OTEL_ENABLED=false)")
        return False

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        resource = Resource.create(
            {
                SERVICE_NAME: service_name,
                SERVICE_VERSION: version,
            }
        )

        provider = TracerProvider(resource=resource)

        otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        if otlp_endpoint:
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

            exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
            logger.info("OTLP trace exporter configured", endpoint=otlp_endpoint)
        else:
            from opentelemetry.sdk.trace.export import ConsoleSpanExporter

            exporter = ConsoleSpanExporter()
            logger.info(
                "Console trace exporter configured (set OTEL_EXPORTER_OTLP_ENDPOINT for OTLP)"
            )

        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)

        _tracing_enabled = True
        logger.info("OpenTelemetry tracing initialized", service=service_name)
        return True

    except ImportError:
        logger.warning("opentelemetry-sdk not installed — tracing unavailable")
        return False
    except Exception as exc:
        logger.error("Failed to initialize tracing", error=str(exc))
        return False


def instrument_fastapi(app: Any) -> None:
    """Instrument FastAPI with OpenTelemetry if tracing is enabled."""
    if not _tracing_enabled:
        return
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        FastAPIInstrumentor.instrument_app(app)
        logger.info("FastAPI instrumented with OpenTelemetry")
    except ImportError:
        logger.warning("opentelemetry-instrumentation-fastapi not installed")
