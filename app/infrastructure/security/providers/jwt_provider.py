import jwt
from datetime import datetime, timezone
from typing import Optional

from app.domain.security.interfaces import IIdentityProvider
from app.domain.security.models import ExecutionContext, AuthenticationResult, AuthenticationStatus
from app.domain.security.config import SecurityConfig
import structlog

logger = structlog.get_logger()

class JWTIdentityProvider(IIdentityProvider):
    """
    Identity Provider that parses and validates JSON Web Tokens (JWT).
    Supports Key ID (kid) resolution for signing keys.
    """
    
    def __init__(self, config: SecurityConfig):
        self._config = config

    @property
    def scheme(self) -> str:
        return "Bearer"

    async def authenticate(self, credentials: str) -> AuthenticationResult:
        try:
            # First decode the unverified headers to get the 'kid' (Key ID)
            unverified_headers = jwt.get_unverified_header(credentials)
            kid = unverified_headers.get("kid", "default")
            
            # Resolve the signing key
            secret = self._config.jwt_keys.get(kid)
            if not secret:
                logger.warning("jwt_kid_not_found", kid=kid)
                return AuthenticationResult.failure(AuthenticationStatus.AUTHENTICATION_FAILED, f"Unknown key ID: {kid}")
                
            # Decode and verify the JWT payload
            payload = jwt.decode(
                credentials, 
                secret, 
                algorithms=["HS256"]
            )
            
            # Build the ExecutionContext
            context = ExecutionContext(
                is_authenticated=True,
                tenant_id=payload.get("tenant_id"),
                user_id=payload.get("sub"), # Standard JWT subject claim
                roles=payload.get("roles", []),
                scopes=payload.get("scopes", []),
                session_id=payload.get("session_id"),
                authentication_method="jwt",
                authenticated_at=datetime.now(timezone.utc)
            )
            return AuthenticationResult.success(context)
            
        except jwt.ExpiredSignatureError:
            logger.warning("jwt_expired")
            return AuthenticationResult.failure(AuthenticationStatus.TOKEN_EXPIRED, "Token has expired")
        except jwt.InvalidTokenError as e:
            logger.warning("jwt_invalid", error=str(e))
            return AuthenticationResult.failure(AuthenticationStatus.INVALID_TOKEN, "Invalid token signature")
        except Exception as e:
            logger.error("jwt_processing_error", error=str(e))
            return AuthenticationResult.failure(AuthenticationStatus.AUTHENTICATION_FAILED, "Authentication failed")
