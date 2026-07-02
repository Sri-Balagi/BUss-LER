from fastapi import APIRouter, Depends, HTTPException

from app.bootstrap.container import get_container
from app.infrastructure.ai.kernel import AbstractAIKernel
from app.interfaces.http.v1.dependencies_ai import get_ai_kernel

api_router = APIRouter()


@api_router.get("/health")
async def health_check():
    """Basic service health check."""
    # Ensure DI container is built and accessible
    try:
        get_container()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DI Container not initialized: {e}")
    return {"status": "ok"}


@api_router.get("/health/ai")
async def ai_health_check(kernel: AbstractAIKernel = Depends(get_ai_kernel)):
    """Deep health check for AI Platform."""
    try:
        status = await kernel.health_check()
        if status.get("status") != "ok":
            raise HTTPException(status_code=503, detail=status)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
