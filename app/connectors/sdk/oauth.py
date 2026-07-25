"""
OAuth Connector SDK interfaces.

Provides ``OAuthConnector`` and ``OAuthPKCEConnector`` abstract classes for
connectors that use OAuth 2.0 authorization flows.

Concrete implementations must override the abstract methods and supply
``_client_id``, ``_client_secret``, ``_auth_url``, ``_token_url``,
and ``_scopes``.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

from app.connectors.sdk.base import (
    AuthType,
    BaseConnector,
    ConnectorHealthResult,
    ConnectorStatus,
    SyncResult,
    SyncType,
    ValidationResult,
    WebhookResult,
)
from app.connectors.sdk.mixins import HealthCheckMixin, SyncMixin


class OAuthConnector(BaseConnector, SyncMixin, HealthCheckMixin):
    """
    Abstract base for OAuth 2.0 Authorization Code Flow connectors.

    Subclasses must implement:
    - ``_build_auth_url()``
    - ``_exchange_code()``
    - ``_refresh_access_token()``
    - ``get_capabilities()``
    - ``health_check()``
    - ``sync()``
    - ``handle_webhook()``
    """

    auth_type: AuthType = AuthType.OAUTH2

    def __init__(
        self,
        connector_id: str,
        profile_id: str | None = None,
        client_id: str = "",
        client_secret: str = "",
        auth_url: str = "",
        token_url: str = "",
        redirect_uri: str = "",
        scopes: list[str] | None = None,
    ) -> None:
        super().__init__(connector_id, profile_id)
        self._client_id = client_id
        self._client_secret = client_secret
        self._auth_url = auth_url
        self._token_url = token_url
        self._redirect_uri = redirect_uri
        self._scopes = scopes or []
        self._access_token: str | None = None
        self._refresh_token_value: str | None = None

    # ------------------------------------------------------------------
    # OAuth-specific abstract methods
    # ------------------------------------------------------------------

    @abstractmethod
    def _build_auth_url(self, state: str) -> str:
        """Return the authorization URL to redirect the user to."""

    @abstractmethod
    async def _exchange_code(self, code: str, state: str) -> dict[str, Any]:
        """Exchange authorization code for tokens. Returns token response dict."""

    @abstractmethod
    async def _refresh_access_token(self) -> dict[str, Any]:
        """Use the refresh token to obtain a new access token."""

    # ------------------------------------------------------------------
    # BaseConnector lifecycle defaults (override as needed)
    # ------------------------------------------------------------------

    async def install(self) -> None:
        self._set_status(ConnectorStatus.INSTALLED)

    async def uninstall(self) -> None:
        self._access_token = None
        self._refresh_token_value = None
        self._set_status(ConnectorStatus.UNINSTALLED)

    async def connect(self) -> None:
        if self._access_token:
            self._set_status(ConnectorStatus.CONNECTED)

    async def disconnect(self) -> None:
        self._set_status(ConnectorStatus.DISCONNECTED)

    async def authenticate(self) -> None:
        """
        Initiates the OAuth flow.
        In practice the ConnectorManager coordinates redirects externally;
        this method handles token storage once the code is received.
        """
        # Token exchange is handled by the auth strategy layer.
        self._set_status(ConnectorStatus.CONFIGURED)

    async def refresh_token(self) -> None:
        token_data = await self._refresh_access_token()
        self._access_token = token_data.get("access_token")
        new_refresh = token_data.get("refresh_token")
        if new_refresh:
            self._refresh_token_value = new_refresh

    async def validate(self) -> ValidationResult:
        result = ValidationResult(valid=True)
        if not self._client_id:
            result.add_error("client_id is required")
        if not self._client_secret:
            result.add_error("client_secret is required")
        if not self._auth_url:
            result.add_error("auth_url is required")
        if not self._token_url:
            result.add_error("token_url is required")
        return result

    async def health_check(self) -> ConnectorHealthResult:
        return await self.run_health_check()

    async def sync(self, sync_type: SyncType = SyncType.INCREMENTAL) -> SyncResult:
        if sync_type == SyncType.FULL:
            return await self.run_full_sync()
        return await self.run_incremental_sync()

    async def handle_webhook(self, payload: dict[str, Any]) -> WebhookResult:
        return WebhookResult(
            connector_id=self._connector_id,
            event_type=payload.get("type", "unknown"),
            processed=False,
            error="handle_webhook not implemented",
        )

    async def shutdown(self) -> None:
        self._set_status(ConnectorStatus.DISCONNECTED)

    def get_capabilities(self) -> list[str]:
        return []


class OAuthPKCEConnector(OAuthConnector):
    """
    Abstract base for OAuth 2.0 PKCE (Proof Key for Code Exchange) connectors.

    Used for public clients (mobile, SPA) where a client secret cannot be
    safely stored. Extends ``OAuthConnector`` with PKCE-specific methods.
    """

    auth_type: AuthType = AuthType.OAUTH2_PKCE

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._code_verifier: str | None = None
        self._code_challenge: str | None = None

    @abstractmethod
    def _generate_pkce_pair(self) -> tuple[str, str]:
        """Generate (code_verifier, code_challenge) PKCE pair."""

    @abstractmethod
    def _build_auth_url(self, state: str) -> str:
        """Build authorization URL including code_challenge."""
