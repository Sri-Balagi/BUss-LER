"""System endpoints for health, liveness, and readiness.

These three endpoints follow Kubernetes probe conventions:
- /health  — basic liveness check (is the process alive?)
- /live    — alias for /health
- /ready   — readiness check (can the process serve traffic?)
"""

from __future__ import annotations

import platform
import time
from typing import Any

import structlog
from fastapi import APIRouter

logger = structlog.get_logger()

# Track startup time for uptime reporting
_start_time = time.time()

router = APIRouter(tags=["System"])


@router.get(
    "/health",
    summary="Health Check",
    description="Basic health check. Returns 200 if the process is alive.",
    response_description="Health status",
)
async def health_check() -> dict[str, Any]:
    """Liveness probe — always returns 200 if the process is running."""
    return {
        "status": "ok",
        "service": "bizos",
        "version": "6.0.0",
        "uptime_seconds": round(time.time() - _start_time, 2),
    }


@router.get(
    "/live",
    summary="Liveness Probe",
    description="Kubernetes liveness probe. Returns 200 if the process is alive.",
)
async def liveness_probe() -> dict[str, str]:
    """Kubernetes liveness probe endpoint."""
    return {"status": "alive"}


@router.get(
    "/ready",
    summary="Readiness Probe",
    description="Kubernetes readiness probe. Returns 200 if the service can handle traffic.",
    responses={
        503: {"description": "Service not ready"},
    },
)
async def readiness_probe() -> dict[str, Any]:
    """Kubernetes readiness probe.

    Returns 503 if the service has not completed startup or is degraded.
    """
    # In the current implementation, if we reach this endpoint, we are ready.
    # Future: check qdrant connectivity, supabase ping, etc.
    return {
        "status": "ready",
        "service": "bizos",
        "python": platform.python_version(),
        "uptime_seconds": round(time.time() - _start_time, 2),
    }


from fastapi import Depends
from app.interfaces.http.v1.dependencies_system import get_system_query_service
from app.application.system.query_service import SystemQueryService
from app.interfaces.http.v1.schemas.response import BizOSResponse


@router.get(
    "/workflows",
    response_model=BizOSResponse[list[dict]],
    summary="List Active Workflows",
)
async def get_active_workflows(
    service: SystemQueryService = Depends(get_system_query_service),
) -> BizOSResponse[list[dict]]:
    """Retrieves active workflows from the runtime environment."""
    data = await service.list_active_workflows()
    return BizOSResponse.ok(data=data)


@router.get(
    "/registries/{registry_name}/items",
    response_model=BizOSResponse[list[dict]],
    summary="List Registry Items",
)
async def get_registry_items(
    registry_name: str,
    service: SystemQueryService = Depends(get_system_query_service),
) -> BizOSResponse[list[dict]]:
    """Retrieves items from a specified registry."""
    from fastapi import HTTPException
    try:
        data = await service.list_registry_items(registry_name)
        return BizOSResponse.ok(data=data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get(
    "/memory",
    response_model=BizOSResponse[dict],
    summary="Get Memory Status",
)
async def get_memory_status(
    service: SystemQueryService = Depends(get_system_query_service),
) -> BizOSResponse[dict]:
    """Retrieves the system's memory subsystem status."""
    data = await service.get_memory_status()
    return BizOSResponse.ok(data=data)

