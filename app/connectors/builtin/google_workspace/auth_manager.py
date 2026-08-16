"""Google Workspace Auth Helper

Provides helper functions for Google Workspace connectors to access the unified OAuth token
using the platform's standard OAuthProviderManager.
"""

from typing import Any, Dict, Optional
import structlog

from app.connectors.oauth.manager import OAuthProviderManager
from app.connectors.sdk.errors import ConnectorError

logger = structlog.get_logger(__name__)

# Scopes are now defined in app.connectors.oauth.providers.google

class GoogleWorkspaceAuthManager:
    """Helper to fetch Google tokens from the unified OAuth manager."""

    @classmethod
    async def get_access_token(
        cls,
        tenant_id: str = "default_tenant",
        account_id: str = "default",
        client_id: str = "",
        client_secret: str = ""
    ) -> str:
        """
        Retrieves a valid Google access token from the platform's OAuthProviderManager.
        Auto-refreshes if expired.
        """
        manager = OAuthProviderManager()
        try:
            token = await manager.get_live_token(
                provider_id="google",
                tenant_id=tenant_id,
                account_id=account_id,
                client_id=client_id,
                client_secret=client_secret
            )
            return token
        except ValueError as e:
            logger.error("Failed to get Google access token", error=str(e))
            raise ConnectorError(f"Authentication required for Google Workspace: {str(e)}")
