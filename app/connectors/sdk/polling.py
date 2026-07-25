"""SDK — Polling Connector base."""
from __future__ import annotations

import asyncio
import logging
from abc import abstractmethod
from datetime import UTC, datetime
from typing import Any

from app.connectors.sdk.base import (
    BaseConnector, ConnectorHealthResult, ConnectorStatus,
    SyncResult, SyncType, ValidationResult, WebhookResult,
)
from app.connectors.sdk.mixins import HealthCheckMixin, SyncMixin

logger = logging.getLogger(__name__)


class PollingConnector(BaseConnector, SyncMixin, HealthCheckMixin):
    """
    Abstract base for poll-based connectors.

    Poll-based connectors periodically fetch new data from external APIs
    rather than receiving push events. The ConnectorScheduler triggers
    ``poll()`` on the configured interval.

    Subclasses must implement:
    - ``poll()``
    - ``get_capabilities()``
    - ``health_check()``
    """

    def __init__(
        self,
        connector_id: str,
        profile_id: str | None = None,
        poll_interval_seconds: int = 300,
    ) -> None:
        super().__init__(connector_id, profile_id)
        self._poll_interval = poll_interval_seconds
        self._last_poll_at: datetime | None = None
        self._polling_task: asyncio.Task[None] | None = None

    @property
    def poll_interval_seconds(self) -> int:
        return self._poll_interval

    @property
    def last_poll_at(self) -> datetime | None:
        return self._last_poll_at

    @abstractmethod
    async def poll(self) -> SyncResult:
        """
        Perform a single poll cycle.
        Implementations should use SyncMixin.run_incremental_sync() for the
        data fetching loop and persist the cursor via the StateStore.
        """

    async def start_polling(self) -> None:
        """Start continuous polling loop. Called by ConnectorScheduler."""
        self._polling_task = asyncio.create_task(self._polling_loop())

    async def stop_polling(self) -> None:
        """Stop the polling loop gracefully."""
        if self._polling_task and not self._polling_task.done():
            self._polling_task.cancel()
            try:
                await self._polling_task
            except asyncio.CancelledError:
                pass
            self._polling_task = None

    async def _polling_loop(self) -> None:
        while True:
            try:
                logger.debug("Polling connector=%s", self._connector_id)
                await self.poll()
                self._last_poll_at = datetime.now(UTC)
            except Exception as e:
                logger.error(
                    "Poll failed connector=%s error=%s", self._connector_id, e
                )
            await asyncio.sleep(self._poll_interval)

    async def sync(self, sync_type: SyncType = SyncType.INCREMENTAL) -> SyncResult:
        return await self.poll()

    async def handle_webhook(self, payload: dict[str, Any]) -> WebhookResult:
        # Polling connectors typically do not handle webhooks.
        return WebhookResult(
            connector_id=self._connector_id,
            event_type="unsupported",
            processed=False,
            error="Polling connectors do not support webhooks",
        )

    async def validate(self) -> ValidationResult:
        result = ValidationResult(valid=True)
        if self._poll_interval < 60:
            result.add_warning("Poll interval < 60s may cause rate limiting")
        return result

    async def health_check(self) -> ConnectorHealthResult:
        return await self.run_health_check()

    async def install(self) -> None:
        self._set_status(ConnectorStatus.INSTALLED)

    async def uninstall(self) -> None:
        await self.stop_polling()
        self._set_status(ConnectorStatus.UNINSTALLED)

    async def connect(self) -> None:
        self._set_status(ConnectorStatus.CONNECTED)

    async def disconnect(self) -> None:
        await self.stop_polling()
        self._set_status(ConnectorStatus.DISCONNECTED)

    async def authenticate(self) -> None:
        self._set_status(ConnectorStatus.CONFIGURED)

    async def refresh_token(self) -> None:
        pass

    async def shutdown(self) -> None:
        await self.stop_polling()
        self._set_status(ConnectorStatus.DISCONNECTED)

    def get_capabilities(self) -> list[str]:
        return []
