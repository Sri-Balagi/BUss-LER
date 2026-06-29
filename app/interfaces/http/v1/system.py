"""System endpoints for health and monitoring."""

from typing import Dict

from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Basic health check endpoint."""
    return {"status": "ok"}
