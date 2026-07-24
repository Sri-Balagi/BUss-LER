from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class ApiLifecycleMiddleware(BaseHTTPMiddleware):
    """
    Manages API versioning and deprecation support.
    Can inject standard HTTP headers like Deprecation and Sunset.
    """

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore
        response = await call_next(request)

        # Example of how we might evaluate endpoint deprecation:
        # If the path matches deprecated v1 paths, we add headers
        # if "/api/v1/legacy" in request.url.path:
        #     response.headers["Deprecation"] = "true"
        #     response.headers["Sunset"] = "Wed, 01 Jan 2027 23:59:59 GMT"

        return response
