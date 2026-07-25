"""SDK — API Key Connector base."""
from __future__ import annotations

from abc import abstractmethod
from typing import Any

from app.connectors.sdk.base import (
    AuthType, BaseConnector, ConnectorHealthResult, ConnectorStatus,
    SyncResult, SyncType, ValidationResult, WebhookResult,
)
from app.connectors.sdk.mixins import HealthCheckMixin, SyncMixin


class APIKeyConnector(BaseConnector, SyncMixin, HealthCheckMixin):
    """
    Abstract base for API Key authenticated connectors.

    The API key is injected at runtime via the SecretVault and should
    never be stored in plaintext in source code or config files.
    """

    auth_type: AuthType = AuthType.API_KEY

    def __init__(
        self,
        connector_id: str,
        profile_id: str | None = None,
        api_key: str = "",
        base_url: str = "",
        key_header: str = "X-API-Key",
    ) -> None:
        super().__init__(connector_id, profile_id)
        self._api_key = api_key
        self._base_url = base_url
        self._key_header = key_header

    @property
    def auth_headers(self) -> dict[str, str]:
        """Returns headers required for authenticated requests."""
        return {self._key_header: self._api_key}

    async def install(self) -> None:
        self._set_status(ConnectorStatus.INSTALLED)

    async def uninstall(self) -> None:
        self._api_key = ""
        self._set_status(ConnectorStatus.UNINSTALLED)

    async def connect(self) -> None:
        if self._api_key:
            self._set_status(ConnectorStatus.CONNECTED)

    async def disconnect(self) -> None:
        self._set_status(ConnectorStatus.DISCONNECTED)

    async def authenticate(self) -> None:
        # API key is loaded from SecretVault by ConnectorManager before connect()
        self._set_status(ConnectorStatus.CONFIGURED)

    async def refresh_token(self) -> None:
        # API keys do not have tokens; this is a no-op by default.
        pass

    async def validate(self) -> ValidationResult:
        result = ValidationResult(valid=True)
        if not self._api_key:
            result.add_error("api_key is required")
        if not self._base_url:
            result.add_error("base_url is required")
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

    @abstractmethod
    async def _ping(self) -> bool:
        """Make a lightweight API call to verify the key is valid."""
