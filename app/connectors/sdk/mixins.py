"""
SDK Mixins — reusable behaviors connectors can inherit without reimplementing.

Usage::

    class MyConnector(OAuthConnector, SyncMixin, HealthCheckMixin):
        ...
"""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

from app.connectors.sdk.base import ConnectorHealthResult, ConnectorStatus, SyncResult, SyncType

logger = logging.getLogger(__name__)


class SyncMixin:
    """
    Provides default sync scaffolding.

    Subclasses override ``_fetch_page()`` and ``_process_record()`` rather than
    reimplementing the entire sync loop.
    """

    _connector_id: str = ""
    _profile_id: str = "default"
    _status: ConnectorStatus = ConnectorStatus.INSTALLED

    async def _fetch_page(
        self,
        cursor: str | None = None,
    ) -> tuple[list[dict[str, Any]], str | None]:
        """
        Fetch one page of records from the external service.

        Returns:
            (records, next_cursor) — next_cursor is None when exhausted.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement _fetch_page()"
        )

    async def _process_record(self, record: dict[str, Any]) -> None:
        """Process and persist a single fetched record."""
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement _process_record()"
        )

    async def run_full_sync(self) -> SyncResult:
        """Execute a complete full sync — iterates all pages."""
        result = SyncResult(
            connector_id=self._connector_id,
            profile_id=self._profile_id,
            sync_type=SyncType.FULL,
        )
        cursor: str | None = None
        try:
            while True:
                records, next_cursor = await self._fetch_page(cursor)
                for record in records:
                    try:
                        await self._process_record(record)
                        result.records_processed += 1
                        result.records_created += 1
                    except Exception as e:
                        result.records_failed += 1
                        logger.warning(
                            "Record processing failed connector=%s error=%s",
                            self._connector_id, e,
                        )
                if next_cursor is None:
                    break
                cursor = next_cursor
            result.success = True
            result.cursor = cursor
            result.completed_at = datetime.now(UTC)
        except Exception as e:
            result.success = False
            result.error = str(e)
            result.completed_at = datetime.now(UTC)
            logger.error(
                "Full sync failed connector=%s error=%s",
                self._connector_id, e,
            )
        return result

    async def run_incremental_sync(self, cursor: str | None = None) -> SyncResult:
        """Execute an incremental sync from the given cursor."""
        result = SyncResult(
            connector_id=self._connector_id,
            profile_id=self._profile_id,
            sync_type=SyncType.INCREMENTAL,
        )
        try:
            records, next_cursor = await self._fetch_page(cursor)
            for record in records:
                try:
                    await self._process_record(record)
                    result.records_processed += 1
                    result.records_updated += 1
                except Exception as e:
                    result.records_failed += 1
                    logger.warning(
                        "Incremental record failed connector=%s error=%s",
                        self._connector_id, e,
                    )
            result.cursor = next_cursor
            result.success = True
            result.completed_at = datetime.now(UTC)
        except Exception as e:
            result.success = False
            result.error = str(e)
            result.completed_at = datetime.now(UTC)
        return result


class HealthCheckMixin:
    """Provides a default connectivity health check implementation."""

    _connector_id: str = ""
    _profile_id: str = "default"
    _status: ConnectorStatus = ConnectorStatus.INSTALLED

    async def _ping(self) -> bool:
        """
        Perform a lightweight ping to verify connectivity.
        Override to make an actual API call (e.g., GET /user or similar).
        """
        return True

    async def run_health_check(self) -> ConnectorHealthResult:
        start = asyncio.get_event_loop().time()
        try:
            alive = await asyncio.wait_for(self._ping(), timeout=5.0)
            latency_ms = (asyncio.get_event_loop().time() - start) * 1000
            return ConnectorHealthResult(
                connector_id=self._connector_id,
                profile_id=self._profile_id,
                healthy=alive,
                status=self._status,
                latency_ms=latency_ms,
                message="OK" if alive else "Ping returned False",
            )
        except asyncio.TimeoutError:
            return ConnectorHealthResult(
                connector_id=self._connector_id,
                profile_id=self._profile_id,
                healthy=False,
                status=ConnectorStatus.DEGRADED,
                message="Health check timed out after 5s",
            )
        except Exception as e:
            return ConnectorHealthResult(
                connector_id=self._connector_id,
                profile_id=self._profile_id,
                healthy=False,
                status=ConnectorStatus.ERROR,
                message=str(e),
            )


class RateLimitMixin:
    """
    Integrates rate limiter from ``app.connectors.ratelimit`` into connector.

    The ConnectorManager injects a ``RateLimiter`` instance at runtime.
    Connectors call ``await self._acquire_rate_limit()`` before any API call.
    """

    _rate_limiter: Any | None = None  # RateLimiter injected at runtime

    async def _acquire_rate_limit(self, tokens: int = 1) -> None:
        if self._rate_limiter is not None:
            await self._rate_limiter.acquire(tokens)

    async def _handle_retry_after(self, retry_after: int) -> None:
        if self._rate_limiter is not None:
            await self._rate_limiter.handle_retry_after(retry_after)
        else:
            await asyncio.sleep(retry_after)


class AuditMixin:
    """Provides structured audit logging for connector operations."""

    _connector_id: str = ""
    _audit_logger: Any | None = None  # ConnectorAuditLogger injected at runtime

    async def _audit(self, action: str, result: str, metadata: dict[str, Any] | None = None) -> None:
        if self._audit_logger is not None:
            await self._audit_logger.log(
                connector_id=self._connector_id,
                action=action,
                result=result,
                metadata=metadata or {},
            )


class CacheMixin:
    """Provides transparent cache access for connector operations."""

    _cache: Any | None = None  # ConnectorCache injected at runtime

    async def _cache_get(self, key: str) -> Any | None:
        if self._cache is not None:
            return await self._cache.get(key)
        return None

    async def _cache_set(self, key: str, value: Any, ttl: int | None = None) -> None:
        if self._cache is not None:
            await self._cache.set(key, value, ttl=ttl)

    async def _cache_invalidate(self, key: str) -> None:
        if self._cache is not None:
            await self._cache.invalidate(key)
