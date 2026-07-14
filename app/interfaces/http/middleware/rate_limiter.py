import time
from collections import defaultdict
from typing import Dict, List

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.interfaces.http.v1.schemas.errors import ErrorCode
from app.interfaces.http.v1.schemas.response import BizOSResponse

# In-memory fallback for rate limiting (if Redis is not available)
# Maps client identifier -> list of timestamps
_in_memory_store: Dict[str, List[float]] = defaultdict(list)

# Limits
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 100


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Implements rate limiting per tenant or IP address.
    Uses Redis in production (not implemented here yet) or in-memory fallback.
    """

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore
        # Identify client (Tenant ID, API Key, or IP)
        client_id = getattr(request.state, "resolved_tenant_id", None)
        if not client_id:
            client_id = request.client.host if request.client else "unknown"

        now = time.time()
        
        # Clean up old timestamps (sliding window)
        _in_memory_store[client_id] = [
            ts for ts in _in_memory_store[client_id] 
            if now - ts < RATE_LIMIT_WINDOW
        ]
        
        if len(_in_memory_store[client_id]) >= RATE_LIMIT_MAX_REQUESTS:
            payload = BizOSResponse.fail(
                code=ErrorCode.RATE_LIMITED.value,
                message="Rate limit exceeded. Please try again later."
            )
            return Response(
                content=payload.model_dump_json(),
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": str(RATE_LIMIT_WINDOW)}
            )
            
        _in_memory_store[client_id].append(now)
        
        return await call_next(request)
