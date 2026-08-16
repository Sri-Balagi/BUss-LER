
import structlog
from fastapi import Depends, HTTPException, status

from app.api.dependencies.auth import get_execution_context
from app.bootstrap.container import get_container
from app.domain.security.interfaces import IPolicyEngine
from app.domain.security.models import ExecutionContext
from app.domain.security.permissions import SystemPermission

logger = structlog.get_logger()

def get_policy_engine() -> IPolicyEngine:
    """Dependency for resolving the IPolicyEngine."""
    container = get_container()
    return container.resolve(IPolicyEngine)

class RequirePermission:
    """
    FastAPI dependency factory that enforces a specific permission.

    Usage:
        @router.get("/workflows", dependencies=[Depends(RequirePermission(SystemPermission.WORKFLOW_READ))])
    """

    def __init__(self, permission: SystemPermission):
        self.permission = permission

    async def __call__(
        self,
        context: ExecutionContext = Depends(get_execution_context),
        engine: IPolicyEngine = Depends(get_policy_engine)
    ) -> ExecutionContext:
        """
        Evaluates the current execution context against the required permission.
        Raises HTTP 401 if anonymous, or 403 if insufficient permissions.
        Returns the ExecutionContext on success.
        """

        # 1. Evaluate Authorization
        decision = await engine.authorize(
            context=context,
            permission=self.permission,
            resource=None # Extensible for resource-level authorization
        )

        # 2. Enforce Decision
        if decision.is_allowed:
            return context

        # 3. Handle Denials
        if not context.is_authenticated:
            # Rejection due to anonymity
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required to perform this action.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Rejection due to insufficient permissions
        logger.warning(
            "authz_forbidden",
            subject=context.user_id or context.api_key_id,
            permission=self.permission.value,
            reason=decision.reason
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Forbidden: Insufficient permissions ({self.permission.value})"
        )
