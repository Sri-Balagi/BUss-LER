"""Connector Health Monitor."""
from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.connectors.sdk.base import BaseConnector

logger = logging.getLogger(__name__)


class ConnectorHealthSnapshot(BaseModel):
    """Point-in-time health snapshot for one connector profile."""

    connector_id: str
    profile_id: str
    healthy: bool
    status: str
    latency_ms: float | None = None
    last_checked: datetime = Field(default_factory=lambda: datetime.now(UTC))
    consecutive_failures: int = 0
    total_checks: int = 0
    message: str = ""
    details: dict[str, Any] = Field(default_factory=dict)


class HealthMonitor:
    """
    Periodically runs health checks on all active connectors.

    Each connector is checked on its own interval (from the manifest).
    Results are stored and exposed via ``get_status()`` and ``get_all_statuses()``.
    """

    def __init__(self, default_interval: int = 60) -> None:
        self._default_interval = default_interval
        self._snapshots: dict[str, ConnectorHealthSnapshot] = {}
        self._tasks: dict[str, asyncio.Task[None]] = {}
        self._connectors: dict[str, BaseConnector] = {}

    def register(
        self,
        connector: BaseConnector,
        interval_seconds: int | None = None,
    ) -> None:
        """Register a connector for health monitoring."""
        key = f"{connector.connector_id}:{connector.profile_id}"
        self._connectors[key] = connector
        interval = interval_seconds or self._default_interval

        if key in self._tasks and not self._tasks[key].done():
            self._tasks[key].cancel()

        self._tasks[key] = asyncio.create_task(
            self._monitoring_loop(connector, interval, key)
        )
        logger.info(
            "HealthMonitor: registered %s[%s] interval=%ds",
            connector.connector_id,
            connector.profile_id,
            interval,
        )

    def unregister(self, connector_id: str, profile_id: str = "default") -> None:
        key = f"{connector_id}:{profile_id}"
        task = self._tasks.pop(key, None)
        if task and not task.done():
            task.cancel()
        self._connectors.pop(key, None)
        self._snapshots.pop(key, None)

    def get_status(
        self,
        connector_id: str,
        profile_id: str = "default",
    ) -> ConnectorHealthSnapshot | None:
        key = f"{connector_id}:{profile_id}"
        return self._snapshots.get(key)

    def get_all_statuses(self) -> list[ConnectorHealthSnapshot]:
        return list(self._snapshots.values())

    def get_unhealthy(self) -> list[ConnectorHealthSnapshot]:
        return [s for s in self._snapshots.values() if not s.healthy]

    async def check_now(
        self,
        connector_id: str,
        profile_id: str = "default",
    ) -> ConnectorHealthSnapshot | None:
        key = f"{connector_id}:{profile_id}"
        connector = self._connectors.get(key)
        if connector is None:
            return None
        return await self._run_check(connector, key)

    async def shutdown(self) -> None:
        for task in self._tasks.values():
            if not task.done():
                task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks.values(), return_exceptions=True)
        self._tasks.clear()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _monitoring_loop(
        self,
        connector: BaseConnector,
        interval: int,
        key: str,
    ) -> None:
        while True:
            await self._run_check(connector, key)
            await asyncio.sleep(interval)

    async def _run_check(
        self,
        connector: BaseConnector,
        key: str,
    ) -> ConnectorHealthSnapshot:
        prev = self._snapshots.get(key)
        failures = prev.consecutive_failures if prev else 0
        total = prev.total_checks if prev else 0

        try:
            result = await asyncio.wait_for(connector.health_check(), timeout=10.0)
            snapshot = ConnectorHealthSnapshot(
                connector_id=connector.connector_id,
                profile_id=connector.profile_id,
                healthy=result.healthy,
                status=result.status.value,
                latency_ms=result.latency_ms,
                consecutive_failures=0 if result.healthy else failures + 1,
                total_checks=total + 1,
                message=result.message,
            )
        except Exception as e:
            snapshot = ConnectorHealthSnapshot(
                connector_id=connector.connector_id,
                profile_id=connector.profile_id,
                healthy=False,
                status="ERROR",
                consecutive_failures=failures + 1,
                total_checks=total + 1,
                message=str(e),
            )

        self._snapshots[key] = snapshot

        if not snapshot.healthy:
            logger.warning(
                "HealthMonitor: UNHEALTHY connector=%s[%s] failures=%d message=%s",
                connector.connector_id,
                connector.profile_id,
                snapshot.consecutive_failures,
                snapshot.message,
            )
        return snapshot
