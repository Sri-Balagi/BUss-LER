import structlog
from fastapi import Depends, Request

from app.bootstrap.container import get_container
from app.domain.security.interfaces import IAuthenticationService
from app.domain.security.models import AuthenticationStatus, ExecutionContext

logger = structlog.get_logger()

async def get_auth_service() -> IAuthenticationService:
    """Dependency to retrieve the AuthenticationService from the DI container."""
    container = get_container()
    return container.resolve(IAuthenticationService)

async def get_execution_context(
    request: Request,
    auth_service: IAuthenticationService = Depends(get_auth_service)
) -> ExecutionContext:
    """
    FastAPI dependency that extracts authentication tokens from the request,
    authenticates the identity, and builds the ExecutionContext.
    """

    auth_header = request.headers.get("Authorization")
    api_key_header = request.headers.get("X-API-Key")

    scheme = None
    credentials = None

    if auth_header:
        parts = auth_header.split(" ")
        if len(parts) == 2:
            scheme = parts[0]
            credentials = parts[1]
    elif api_key_header:
        scheme = "ApiKey"
        credentials = api_key_header

    if not scheme or not credentials:
        # For now, return an anonymous context instead of HTTP 401.
        # Authorization policies in Wave-4 M3 will decide if anonymous is allowed.
        return ExecutionContext.anonymous()

    try:
        result = await auth_service.authenticate(scheme=scheme, credentials=credentials)

        # If authentication failed, we could raise an HTTPException here or return anonymous.
        # Following the previous design, return anonymous context for now until AuthZ handles it.
        # In a real system, we might want to log `result.status` and `result.message`.
        if result.status != AuthenticationStatus.SUCCESS or result.context is None:
            logger.info("authentication_failed", status=result.status.value, message=result.message)
            return ExecutionContext.anonymous()

        context = result.context

        # Hydrate the context with observability metadata
        # (Assuming middleware adds these to request.state, or we extract from headers)
        request_id = request.headers.get("X-Request-Id")
        correlation_id = request.headers.get("X-Correlation-Id")

        # We can't mutate the frozen dataclass easily, so we replace it:
        from dataclasses import replace
        context = replace(
            context,
            request_id=request_id,
            correlation_id=correlation_id
        )

        return context

    except Exception as e:
        logger.error("authentication_failure", error=str(e))
        return ExecutionContext.anonymous()
