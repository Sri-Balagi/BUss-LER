from datetime import datetime, timezone
from typing import Optional
import structlog

from app.domain.security.interfaces import IIdentityProvider, IHasher
from app.domain.security.models import ExecutionContext, AuthenticationResult, AuthenticationStatus
from app.domain.identity.interfaces import IAPIKeyRepository

logger = structlog.get_logger()

class APIKeyIdentityProvider(IIdentityProvider):
    """
    Identity Provider that authenticates using an API Key.
    Retrieves the key metadata by prefix and verifies the hash.
    """
    
    def __init__(self, repo: IAPIKeyRepository, hasher: IHasher):
        self._repo = repo
        self._hasher = hasher

    @property
    def scheme(self) -> str:
        return "ApiKey"

    async def authenticate(self, credentials: str) -> AuthenticationResult:
        # Credentials should be the raw api key, which is usually prefix.rest_of_key
        # According to APIKey model: prefix is the first 8 characters.
        if not credentials or len(credentials) < 8:
            logger.warning("api_key_too_short")
            return AuthenticationResult.failure(AuthenticationStatus.INVALID_TOKEN, "API Key too short")
            
        prefix = credentials[:8]
        
        # Look up key by prefix
        api_key = await self._repo.get_by_prefix(prefix)
        if not api_key:
            logger.warning("api_key_not_found", prefix=prefix)
            return AuthenticationResult.failure(AuthenticationStatus.AUTHENTICATION_FAILED, "API Key not found")
            
        if not api_key.is_valid():
            logger.warning("api_key_invalid_state", prefix=prefix, status=api_key.status.value)
            return AuthenticationResult.failure(AuthenticationStatus.REVOKED, f"API Key in invalid state: {api_key.status.value}")
            
        # Verify the hash
        if not self._hasher.verify(credentials, api_key.key_hash):
            logger.warning("api_key_hash_mismatch", prefix=prefix)
            return AuthenticationResult.failure(AuthenticationStatus.INVALID_TOKEN, "API Key hash mismatch")
            
        # Build the ExecutionContext
        context = ExecutionContext(
            is_authenticated=True,
            api_key_id=str(api_key.id),
            roles=[], # Usually API Keys act on behalf of a system or have roles assigned, handled by AuthZ
            scopes=api_key.scopes,
            authentication_method="api_key",
            authenticated_at=datetime.now(timezone.utc)
        )
        return AuthenticationResult.success(context)
