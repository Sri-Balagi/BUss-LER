from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class GatewayAuthMiddleware(BaseHTTPMiddleware):
    """Middleware for handling Authentication at the Application Gateway."""
    async def dispatch(self, request: Request, call_next):
        # Allow health checks without auth
        if request.url.path == "/health":
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Missing or invalid authorization token"})

        token = auth_header.split(" ")[1]
        if token != "valid-test-token":
            # For this milestone, we just use a dummy token validation
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})

        request.state.user_id = "user-123"
        request.state.tenant_id = "tenant-456"

        return await call_next(request)
