"""BizOS API v1 Router — Wave-0 Complete.

Registered subsystems:
    Milestone 1: /entities  /twins
    Milestone 2: /memories
    Milestone 3: /intents   /goals
    Milestone 4: /context   /conversations
    Milestone 5: /plans     /recommendations
    Milestone 6: /traces    /health  /health/ai
"""

from fastapi import APIRouter, Depends, HTTPException

from app.bootstrap.container import get_container
from app.infrastructure.ai.kernel import AbstractAIKernel
from app.interfaces.http.v1.dependencies_ai import get_ai_kernel

# ── Milestone 1 ──────────────────────────────────────────────────────────────
from app.interfaces.http.v1.entities import router as entities_router
from app.interfaces.http.v1.twins import router as twins_router

# ── Milestone 2 ──────────────────────────────────────────────────────────────
from app.interfaces.http.v1.memories import router as memories_router

# ── Milestone 3 ──────────────────────────────────────────────────────────────
from app.interfaces.http.v1.intents import router as intents_router
from app.interfaces.http.v1.goals import router as goals_router

# ── Milestone 4 ──────────────────────────────────────────────────────────────
from app.interfaces.http.v1.context import router as context_router
from app.interfaces.http.v1.conversations import router as conversations_router

# ── Milestone 5 ──────────────────────────────────────────────────────────────
from app.interfaces.http.v1.plans import router as plans_router
from app.interfaces.http.v1.recommendations import router as recommendations_router

# ── Milestone 6 ──────────────────────────────────────────────────────────────
from app.interfaces.http.v1.traces import router as traces_router
from app.interfaces.http.v1.system import router as system_router

api_router = APIRouter()

# Milestone 1 — Digital Twin Foundation
api_router.include_router(entities_router)
api_router.include_router(twins_router)

# Milestone 2 — Memory Engine
api_router.include_router(memories_router)

# Milestone 3 — Intent + Goal Engine
api_router.include_router(intents_router)
api_router.include_router(goals_router)

# Milestone 4 — Context + Conversation Engine
api_router.include_router(context_router)
api_router.include_router(conversations_router)

# Milestone 5 — Planning + Recommendation Engine
api_router.include_router(plans_router)
api_router.include_router(recommendations_router)

# Milestone 6 — Observability
api_router.include_router(traces_router)

# System
api_router.include_router(system_router)



@api_router.get("/health/ai", tags=["System"])
async def ai_health_check(kernel: AbstractAIKernel = Depends(get_ai_kernel)):
    """Deep health check — verifies AI Kernel is reachable and operational."""
    try:
        status = await kernel.health_check()
        if status.get("status") != "ok":
            raise HTTPException(status_code=503, detail=status)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
