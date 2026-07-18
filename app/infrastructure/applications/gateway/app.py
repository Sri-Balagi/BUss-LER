from fastapi import FastAPI

from app.infrastructure.applications.gateway.middleware.tracing import OpenTelemetryMiddleware
from app.infrastructure.applications.gateway.middleware.auth import GatewayAuthMiddleware
from app.infrastructure.applications.gateway.routers import health, apps, events, approvals, sessions

def create_gateway_app() -> FastAPI:
    """Create and configure the Unified Cognitive Gateway FastAPI application."""
    app = FastAPI(
        title="BizOS Cognitive Gateway",
        description="Unified API Gateway for Wave 6/7 Cognitive Applications",
        version="1.1.0"
    )

    # Add middlewares
    app.add_middleware(GatewayAuthMiddleware)
    app.add_middleware(OpenTelemetryMiddleware)

    # Register routers
    app.include_router(health.router)
    app.include_router(apps.router)
    app.include_router(events.router, prefix="/api/v1")
    app.include_router(approvals.router, prefix="/api/v1")
    app.include_router(sessions.router, prefix="/api/v1")

    return app
