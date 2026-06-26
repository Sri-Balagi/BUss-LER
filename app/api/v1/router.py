"""Main router for API v1.

Aggregates all v1 endpoints into a single router.
"""

from fastapi import APIRouter

from app.api.v1.entities import router as entities_router
from app.api.v1.system import router as system_router
from app.api.v1.twins import router as twins_router
from app.api.v1.routers.health import router as health_router
from app.api.v1.routers.memory import router as memory_router

# M3 Routers
from app.api.v1.routers.intent import router as intent_router
from app.api.v1.routers.goals import router as goal_router
from app.api.v1.routers.plans import router as plan_router
from app.api.v1.routers.recommendations import router as recommendation_router
from app.api.v1.routers.cognitive_traces import router as cognitive_trace_router

# Main API v1 router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(system_router)
api_router.include_router(entities_router)
api_router.include_router(twins_router)
api_router.include_router(health_router)
api_router.include_router(memory_router)

# Include M3 Intent Engine routers
api_router.include_router(intent_router)
api_router.include_router(goal_router)
api_router.include_router(plan_router)
api_router.include_router(recommendation_router)
api_router.include_router(cognitive_trace_router)
