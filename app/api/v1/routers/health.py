import time
from typing import Dict, Any

from fastapi import APIRouter, Depends, status

from app.api.v1.dependencies import get_memory_service
from app.services.memory_service import MemoryService


router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/memory", response_model=Dict[str, Any])
async def check_memory_health(
    service: MemoryService = Depends(get_memory_service),
) -> Dict[str, Any]:
    """Check the health of all Memory Engine subsystems."""
    return await service.check_health()
