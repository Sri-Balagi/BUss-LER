import structlog
from typing import List

from app.domain.security.interfaces import IAuthenticationService, IIdentityProvider, IAuditPublisher
from app.domain.security.models import ExecutionContext, AuthenticationResult, AuthenticationStatus
from app.shared.exceptions.errors import ServiceError
from app.shared.events.models import SecurityEvent, AuditCategory
from dataclasses import asdict
import uuid

logger = structlog.get_logger()

class AuthenticationError(ServiceError):
    """Raised when authentication fails unexpectedly or scheme is entirely unsupported."""
    pass

class AuthenticationService(IAuthenticationService):
    """
    Orchestrates authentication by finding the correct provider for the scheme.
    """
    
    def __init__(self, providers: List[IIdentityProvider], audit_publisher: IAuditPublisher | None = None):
        self._providers = {provider.scheme.lower(): provider for provider in providers}
        self._audit_publisher = audit_publisher

    def _emit_audit(self, result: AuthenticationResult, credentials: str) -> None:
        if not self._audit_publisher:
            return
            
        action = "AUTHENTICATE"
        event_result = "SUCCESS" if result.status == AuthenticationStatus.SUCCESS else "FAILURE"
        metadata = {"scheme": result.context.authentication_method if result.context else "unknown", "status": result.status.value, "message": result.message}
        
        ctx_dict = asdict(result.context) if result.context else None
        
        event = SecurityEvent(
            correlation_id=result.context.correlation_id if result.context and result.context.correlation_id else str(uuid.uuid4()),
            category=AuditCategory.AUTHENTICATION,
            action=action,
            result=event_result,
            execution_context=ctx_dict,
            user_id=str(result.context.user_id) if result.context and result.context.user_id else None,
            tenant_id=str(result.context.tenant_id) if result.context and result.context.tenant_id else None,
            metadata=metadata,
            severity="INFO" if event_result == "SUCCESS" else "WARNING"
        )
        self._audit_publisher.publish_audit(event)

    async def authenticate(self, scheme: str, credentials: str) -> AuthenticationResult:
        provider = self._providers.get(scheme.lower())
        
        if not provider:
            logger.warning("auth_scheme_unsupported", scheme=scheme)
            result = AuthenticationResult.failure(AuthenticationStatus.UNSUPPORTED_SCHEME, f"Unsupported authentication scheme: {scheme}")
            self._emit_audit(result, credentials)
            return result
            
        try:
            result = await provider.authenticate(credentials)
            self._emit_audit(result, credentials)
            return result
        except Exception as e:
            logger.error("auth_provider_error", scheme=scheme, error=str(e))
            result = AuthenticationResult.failure(AuthenticationStatus.AUTHENTICATION_FAILED, f"Authentication error: {str(e)}")
            self._emit_audit(result, credentials)
            return result
