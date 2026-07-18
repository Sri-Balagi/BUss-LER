from fastapi import FastAPI

from app.infrastructure.applications.gateway.middleware.tracing import OpenTelemetryMiddleware
from app.infrastructure.applications.gateway.middleware.auth import GatewayAuthMiddleware
from app.infrastructure.applications.gateway.routers import health, apps

def create_gateway_app() -> FastAPI:
    """Create and configure the Unified Cognitive Gateway FastAPI application."""
    app = FastAPI(
        title="BizOS Cognitive Gateway",
        description="Unified API Gateway for Wave 6 Cognitive Applications",
        version="1.0.0"
    )

    # Add middlewares
    app.add_middleware(GatewayAuthMiddleware)
    app.add_middleware(OpenTelemetryMiddleware)

    # Register routers
    app.include_router(health.router)
    app.include_router(apps.router)

    return app
