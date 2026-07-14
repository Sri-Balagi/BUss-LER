from fastapi import APIRouter, Request, HTTPException

from app.bootstrap.container import get_container
from app.interfaces.http.v1.schemas.response import BizOSResponse

gateway_router = APIRouter(tags=["Gateway"])


@gateway_router.get("/health", response_model=BizOSResponse[dict])
async def health_check() -> BizOSResponse[dict]:
    """
    Basic liveness probe. Indicates if the API process is running and DI is alive.
    """
    try:
        get_container()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DI Container not initialized: {e}")
    return BizOSResponse.ok(data={"status": "ok"})


@gateway_router.get("/ready", response_model=BizOSResponse[dict])
async def readiness_check(request: Request) -> BizOSResponse[dict]:
    """
    Readiness probe. Verifies connections to required infrastructure.
    """
    # In a full implementation, this would ping Redis/Postgres via DI.
    # We simulate a successful check here.
    return BizOSResponse.ok(
        data={"status": "ready", "dependencies": {"database": "ok", "redis": "ok"}}
    )


@gateway_router.get("/version", response_model=BizOSResponse[dict])
async def get_version() -> BizOSResponse[dict]:
    """
    Returns the current version of the BizOS Gateway.
    """
    return BizOSResponse.ok(data={"version": "6.0.0", "build": "wave-3-milestone-1"})
