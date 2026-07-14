"""BizOS v6.0.0 — API Entry Point.

Initializes the FastAPI application with:
- Middleware: Request IDs, Security Headers, Prometheus Metrics, CORS, Logging
- Lifecycle: Startup validation, graceful shutdown
- Routers: v1 API, /metrics endpoint
- Observability: Structlog, optional OpenTelemetry

Architecture note: This file is in the interfaces layer.
It must not import from app.runtime or app.intelligence directly.
All kernel access is via app.bootstrap or app.interfaces.http.v1.dependencies.
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from qdrant_client import AsyncQdrantClient
from supabase import AsyncClient

from app.bootstrap.container import build_container, reset_container_for_testing
from app.config import get_settings
from app.infrastructure.persistence.postgres.supabase import SupabaseService
from app.infrastructure.vectorstore.qdrant import QdrantService
from app.interfaces.http.errors import register_exception_handlers
from app.interfaces.http.metrics import MetricsMiddleware, metrics_endpoint
from app.interfaces.http.middleware.request_id import RequestIDMiddleware
from app.interfaces.http.middleware.security_headers import SecurityHeadersMiddleware
from app.interfaces.http.middleware.pipeline import register_gateway_pipeline
from app.interfaces.http.openapi import custom_openapi
from app.interfaces.http.v1.routers.gateway import gateway_router
from app.interfaces.http.v1.router import api_router
from app.platform.resilience.graceful_shutdown import register_shutdown_handlers
from app.platform.telemetry.otel import instrument_fastapi, setup_tracing

logger = structlog.get_logger()


# ── Lifespan ──────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[type-arg]
    """Application lifecycle manager.

    Handles startup validation and graceful shutdown.
    Fails fast if mandatory configuration or infrastructure is invalid.
    """
    settings = get_settings()

    logger.info(
        "Starting BizOS API",
        version="6.0.0",
        env=settings.app_env,
        debug=settings.app_debug,
    )

    try:
        # Register OS-level signal handlers for graceful shutdown
        register_shutdown_handlers()

        # Build container
        logger.info("Building DI container")
        container = build_container()

        # Validate mandatory infrastructure on startup
        logger.info("Initializing Supabase client")
        supabase_client = await SupabaseService.get_client(settings)
        container.register_singleton(AsyncClient, supabase_client)

        logger.info("Initializing Qdrant client and collections")
        await QdrantService.initialize_collections(settings)
        qdrant_client = QdrantService.get_client(settings)
        container.register_singleton(AsyncQdrantClient, qdrant_client)

        logger.info("Validating Dependency Graph")
        from app.infrastructure.ai.budgets.interfaces import IResourceBudget
        from app.infrastructure.ai.kernel import AbstractAIKernel
        from app.infrastructure.ai.prompts.registry import PromptRegistry
        from app.infrastructure.ai.registry import ProviderRegistry
        from app.infrastructure.ai.router import ProviderRouter

        # Resolve critical paths to ensure graph is acyclic and valid
        container.resolve(AbstractAIKernel)
        container.resolve(ProviderRouter)
        container.resolve(ProviderRegistry)
        container.resolve(PromptRegistry)
        container.resolve(IResourceBudget)

        logger.info("Startup complete — BizOS is ready to serve requests")
        yield

    except Exception as exc:
        # Fail fast: do not start serving if infrastructure is unavailable
        logger.error("Startup failed — aborting", error=str(exc))
        raise
    finally:
        logger.info("Shutting down BizOS API")
        await QdrantService.close()
        reset_container_for_testing()


# ── Application Factory ───────────────────────────────────────────────────────


def create_app() -> FastAPI:
    """Factory function to create the FastAPI application instance."""
    settings = get_settings()

    # Initialize optional OpenTelemetry tracing (no-op if OTEL_ENABLED=false)
    setup_tracing(service_name="bizos", version="6.0.0")

    app = FastAPI(
        title="BizOS API",
        description="AI Operating System for Entities — v6.0.0",
        version="6.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.app_debug else None,
        redoc_url="/redoc" if settings.app_debug else None,
        openapi_url="/openapi.json" if settings.app_debug else None,
    )

    # ── Middleware (applied in reverse registration order) ────────────────────
    
    # 1. Security headers (outermost — always applied last in response chain)
    app.add_middleware(SecurityHeadersMiddleware)

    # 2. Prometheus metrics collection
    app.add_middleware(MetricsMiddleware)

    # 3. CORS
    cors_origins = (
        ["*"] if not settings.is_production else settings.model_fields.get("cors_origins", ["*"])  # type: ignore[arg-type]
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # 4. Gateway Request Pipeline (Auth, Tenant, Rate Limiting, Idempotency, Context)
    register_gateway_pipeline(app)

    # ── Request Logging ───────────────────────────────────────────────────────
    @app.middleware("http")
    async def log_requests(request: Request, call_next):  # type: ignore[type-arg]
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start

        # Exclude noisy health probes from access logs
        if request.url.path not in {"/api/v1/health", "/api/v1/live"}:
            logger.info(
                "http.request",
                method=request.method,
                path=request.url.path,
                status=response.status_code,
                duration_ms=round(duration * 1000, 2),
                request_id=getattr(request.state, "request_id", None),
                correlation_id=getattr(request.state, "correlation_id", None),
            )

        return response

    # ── Prometheus /metrics endpoint ──────────────────────────────────────────
    @app.get("/metrics", include_in_schema=False)
    async def _metrics(request: Request) -> Response:
        return metrics_endpoint(request)

    # ── Exception Handlers ────────────────────────────────────────────────────
    register_exception_handlers(app)

    # ── API Routers ───────────────────────────────────────────────────────────
    from app.interfaces.http.v1.routers.mcp import mcp_router
    app.include_router(gateway_router, prefix="/api/v1")
    app.include_router(mcp_router, prefix="/api/v1/mcp")
    app.include_router(api_router, prefix="/api/v1")

    # ── OpenAPI Customization ─────────────────────────────────────────────────
    app.openapi = lambda: custom_openapi(app)  # type: ignore

    # ── Instrument with OTEL (if enabled) ────────────────────────────────────
    instrument_fastapi(app)

    return app


# ── Default Application Instance ─────────────────────────────────────────────
app = create_app()
