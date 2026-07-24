import time
from collections import defaultdict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.interfaces.http.v1.schemas.errors import ErrorCode
from app.interfaces.http.v1.schemas.response import BizOSResponse

# In-memory fallback for rate limiting (if Redis is not available)
# Maps client identifier -> list of timestamps
_in_memory_store: dict[str, list[float]] = defaultdict(list)

# Limits
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 100


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Implements rate limiting per tenant or IP address.
    Uses Redis if REDIS_URL is available, otherwise in-memory fallback.
    """

    def __init__(self, app):
        super().__init__(app)
        import os
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            from redis.asyncio import Redis
            self.redis = Redis.from_url(redis_url, decode_responses=True)
        else:
            self.redis = None

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore
        # Identify client (Tenant ID, API Key, or IP)
        client_id = getattr(request.state, "resolved_tenant_id", None)
        if not client_id:
            client_id = request.client.host if request.client else "unknown"

        now = time.time()

        if self.redis:
            key = f"rate_limit:{client_id}"
            async with self.redis.pipeline(transaction=True) as pipe:
                await pipe.zremrangebyscore(key, 0, now - RATE_LIMIT_WINDOW)
                await pipe.zcard(key)
                await pipe.zadd(key, {str(now): now})
                await pipe.expire(key, RATE_LIMIT_WINDOW)
                results = await pipe.execute()

            request_count = results[1]
            if request_count >= RATE_LIMIT_MAX_REQUESTS:
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
        else:
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
