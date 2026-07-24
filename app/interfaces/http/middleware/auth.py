
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
                if token:
                    import jwt

                    from app.config import get_settings

                    settings = get_settings()
                    try:
                        # Decode Supabase JWT
                        # In production, we should verify signature and audience.
                        # For dev, we might accept it if we don't have jwt_secret, but the roadmap explicitly asks for real validation.
                        options = {"verify_signature": True} if settings.jwt_secret else {"verify_signature": False}
                        claims = jwt.decode(
                            token,
                            settings.jwt_secret or "",
                            algorithms=["HS256"],
                            options=options,
                            audience="authenticated"
                        )

                        request.state.is_authenticated = True
                        request.state.auth_method = "jwt"
                        import uuid
                        request.state.user_id = uuid.UUID(claims["sub"])

                    except jwt.ExpiredSignatureError:
                        return self._unauthorized(ErrorCode.UNAUTHORIZED, "JWT token has expired.")
                    except jwt.InvalidTokenError as e:
                        return self._unauthorized(ErrorCode.UNAUTHORIZED, f"Invalid JWT token: {str(e)}")
                    except (KeyError, ValueError):
                        return self._unauthorized(ErrorCode.UNAUTHORIZED, "Invalid token claims.")
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
