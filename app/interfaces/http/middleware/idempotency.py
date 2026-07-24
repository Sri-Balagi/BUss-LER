
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# In-memory fallback for idempotency keys
# Maps Idempotency-Key -> (Status Code, Headers, Body)
_idempotency_store: dict[str, tuple[int, dict, bytes]] = {}


class IdempotencyMiddleware(BaseHTTPMiddleware):
    """
    Enforces safe retries for mutating operations (POST, PUT, PATCH, DELETE)
    using the 'Idempotency-Key' header.
    """

    def __init__(self, app):
        super().__init__(app)
        import os
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            from redis.asyncio import Redis
            self.redis = Redis.from_url(redis_url, decode_responses=False)
        else:
            self.redis = None

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore
        if request.method not in ("POST", "PUT", "PATCH", "DELETE"):
            return await call_next(request)

        idempotency_key = request.headers.get("Idempotency-Key")
        if not idempotency_key:
            # Idempotency is optional by default, but this middleware
            # hooks into it if provided.
            return await call_next(request)

        redis_key = f"idempotency:{idempotency_key}"

        # Check cache
        if self.redis:
            import json
            cached = await self.redis.get(redis_key)
            if cached:
                data = json.loads(cached.decode("utf-8"))
                status_code = data["status_code"]
                headers = data["headers"]
                body = data["body"].encode("utf-8") if isinstance(data["body"], str) else bytes(data["body"])
                return Response(
                    content=body,
                    status_code=status_code,
                    headers=headers
                )
        else:
            if idempotency_key in _idempotency_store:
                status_code, headers, body = _idempotency_store[idempotency_key]

                # Reconstruct response
                return Response(
                    content=body,
                    status_code=status_code,
                    headers=headers
                )

        # Execute downstream
        response = await call_next(request)

        # We can only cache responses if we consume the body.
        # This is a simplified in-memory cache for the response body.
        # Note: In a production ASGI middleware, consuming a StreamingResponse body is complex.
        # For this milestone, we'll cache non-streaming responses or buffer them.

        body = b""
        async for chunk in response.body_iterator:
            body += chunk

        # Reconstruct response so it can be returned
        cached_response = Response(
            content=body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type
        )

        # Save to cache if successful (2xx)
        if 200 <= response.status_code < 300:
            if self.redis:
                import json
                data = {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "body": body.decode("utf-8", errors="replace")
                }
                await self.redis.set(redis_key, json.dumps(data), ex=86400)
            else:
                _idempotency_store[idempotency_key] = (
                    response.status_code,
                    dict(response.headers),
                    body
                )

        return cached_response
