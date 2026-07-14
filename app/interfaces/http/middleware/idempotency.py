import json
from typing import Dict, Optional, Tuple

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

from app.interfaces.http.v1.schemas.errors import ErrorCode
from app.interfaces.http.v1.schemas.response import BizOSResponse

# In-memory fallback for idempotency keys
# Maps Idempotency-Key -> (Status Code, Headers, Body)
_idempotency_store: Dict[str, Tuple[int, dict, bytes]] = {}


class IdempotencyMiddleware(BaseHTTPMiddleware):
    """
    Enforces safe retries for mutating operations (POST, PUT, PATCH, DELETE)
    using the 'Idempotency-Key' header.
    """

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore
        if request.method not in ("POST", "PUT", "PATCH", "DELETE"):
            return await call_next(request)

        idempotency_key = request.headers.get("Idempotency-Key")
        if not idempotency_key:
            # Idempotency is optional by default, but this middleware 
            # hooks into it if provided.
            return await call_next(request)

        # Check cache
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
            _idempotency_store[idempotency_key] = (
                response.status_code, 
                dict(response.headers), 
                body
            )

        return cached_response
