"""SDK — Webhook Connector base."""
from __future__ import annotations

from abc import abstractmethod
from typing import Any

from app.connectors.sdk.base import (
    BaseConnector, ConnectorHealthResult, ConnectorStatus,
    SyncResult, SyncType, ValidationResult, WebhookResult,
)
from app.connectors.sdk.mixins import HealthCheckMixin


class WebhookConnector(BaseConnector, HealthCheckMixin):
    """
    Abstract base for push-based (webhook-driven) connectors.

    The external service sends events to BizOS via HTTP POST.
    The WebhookRouter verifies signatures then calls ``handle_webhook()``.

    Subclasses must implement:
    - ``_verify_signature()``
    - ``_route_event()``
    - ``get_capabilities()``
    - ``health_check()``
    """

    def __init__(
        self,
        connector_id: str,
        profile_id: str | None = None,
        webhook_secret: str = "",
    ) -> None:
        super().__init__(connector_id, profile_id)
        self._webhook_secret = webhook_secret
        self._registered_webhook_id: str | None = None

    @abstractmethod
    def _verify_signature(
        self,
        payload_bytes: bytes,
        signature_header: str,
    ) -> bool:
        """
        Verify the webhook signature using HMAC or vendor-specific method.
        Returns True if valid, False otherwise.
        """

    @abstractmethod
    async def _route_event(self, event_type: str, payload: dict[str, Any]) -> None:
        """
        Route a verified event payload to the appropriate domain handler.
        Implementations should publish a domain event to the SystemBus.
        """

    async def handle_webhook(self, payload: dict[str, Any]) -> WebhookResult:
        event_type = payload.get("type") or payload.get("event") or "unknown"
        try:
            await self._route_event(str(event_type), payload)
            return WebhookResult(
                connector_id=self._connector_id,
                event_type=str(event_type),
                processed=True,
            )
        except Exception as e:
            return WebhookResult(
                connector_id=self._connector_id,
                event_type=str(event_type),
                processed=False,
                error=str(e),
            )

    async def sync(self, sync_type: SyncType = SyncType.INCREMENTAL) -> SyncResult:
        # Webhook connectors are push-based; sync is a no-op by default.
        return SyncResult(
            connector_id=self._connector_id,
            profile_id=self._profile_id,
            sync_type=sync_type,
            success=True,
            records_processed=0,
        )

    async def validate(self) -> ValidationResult:
        result = ValidationResult(valid=True)
        if not self._webhook_secret:
            result.add_warning("webhook_secret not configured — signatures will not be verified")
        return result

    async def health_check(self) -> ConnectorHealthResult:
        return await self.run_health_check()

    async def install(self) -> None:
        self._set_status(ConnectorStatus.INSTALLED)

    async def uninstall(self) -> None:
        self._set_status(ConnectorStatus.UNINSTALLED)

    async def connect(self) -> None:
        self._set_status(ConnectorStatus.CONNECTED)

    async def disconnect(self) -> None:
        self._set_status(ConnectorStatus.DISCONNECTED)

    async def authenticate(self) -> None:
        self._set_status(ConnectorStatus.CONFIGURED)

    async def refresh_token(self) -> None:
        pass

    async def shutdown(self) -> None:
        self._set_status(ConnectorStatus.DISCONNECTED)

    def get_capabilities(self) -> list[str]:
        return []
