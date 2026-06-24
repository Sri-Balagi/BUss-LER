"""Main router for API v1.

Aggregates all v1 endpoints into a single router.
"""

from fastapi import APIRouter

from app.api.v1.system import router as system_router

# Main API v1 router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(system_router)
# Future endpoints will be added here (entities, memories, goals, etc.)
