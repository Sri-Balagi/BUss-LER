"""BizOS API entry point.

Initializes the FastAPI application, configures middleware, sets up the
lifespan context manager for external service initialization, and
registers all API routers.
"""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config import get_settings
from app.services.qdrant import QdrantService
from app.services.supabase import SupabaseService

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the FastAPI application.
    
    Handles startup and shutdown events for external service connections.
    """
    settings = get_settings()
    logger.info("Starting BizOS API", env=settings.app_env)

    try:
        # Initialize Supabase client
        logger.info("Initializing Supabase client")
        await SupabaseService.get_client(settings)

        # Initialize Qdrant client and collections
        logger.info("Initializing Qdrant client and collections")
        await QdrantService.initialize_collections(settings)
        
        logger.info("Startup complete")
        yield
        
    finally:
        # Graceful shutdown
        logger.info("Shutting down BizOS API")
        await QdrantService.close()


def create_app() -> FastAPI:
    """Factory function to create the FastAPI application instance."""
    settings = get_settings()
    
    app = FastAPI(
        title="BizOS API",
        description="AI Operating System for Entities",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.app_debug else None,
        redoc_url="/redoc" if settings.app_debug else None,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: Restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(api_router, prefix="/api/v1")

    return app


# The default application instance
app = create_app()
