from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.interfaces.http.v1.schemas.errors import ErrorCode
from app.interfaces.http.v1.schemas.response import BizOSResponse


class TenantResolutionMiddleware(BaseHTTPMiddleware):
    """
    Resolves the Tenant for the current request.
    Extracts tenant from X-Tenant-ID header or authentication claims.
    """

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore
        tenant_id = request.headers.get("X-Tenant-ID")
        
        # If no explicit header, attempt to pull from auth context
        # (Assuming auth middleware populated it, or it will be extracted here)
        if not tenant_id and getattr(request.state, "is_authenticated", False):
            # Placeholder for JWT claim extraction or API Key lookup
            pass
            
        request.state.resolved_tenant_id = tenant_id

        # We do not strictly fail here if tenant_id is missing, 
        # because some endpoints (like health/version) are tenant-agnostic.
        # Router dependencies should enforce tenant existence if required.
        
        return await call_next(request)
