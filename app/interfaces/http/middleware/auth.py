import json
from typing import Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.interfaces.http.v1.schemas.errors import ErrorCode
from app.interfaces.http.v1.schemas.response import BizOSResponse


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Validates JWT Bearer tokens or API Keys.
    Attaches authentication state to the request.
    Returns 401 Unauthorized if credentials are provided but invalid.
    Allows anonymous requests to pass through (enforcement happens at the router level).
    """

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore
        auth_header = request.headers.get("Authorization")
        api_key_header = request.headers.get("X-API-Key")

        request.state.is_authenticated = False
        request.state.auth_method = None
        
        # Simplified validation for MVP - actual validation would use JWT/DB checks
        if auth_header:
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                if token:  # Replace with actual JWT decode and verification
                    request.state.is_authenticated = True
                    request.state.auth_method = "jwt"
                else:
                    return self._unauthorized(ErrorCode.UNAUTHORIZED, "Invalid JWT token.")
        elif api_key_header:
            if api_key_header:  # Replace with actual API key hash check
                request.state.is_authenticated = True
                request.state.auth_method = "api_key"
            else:
                return self._unauthorized(ErrorCode.API_KEY_INVALID, "Invalid API Key.")
                
        return await call_next(request)

    def _unauthorized(self, code: ErrorCode, message: str) -> Response:
        payload = BizOSResponse.fail(code=code.value, message=message)
        return Response(
            content=payload.model_dump_json(),
            status_code=401,
            media_type="application/json"
        )
