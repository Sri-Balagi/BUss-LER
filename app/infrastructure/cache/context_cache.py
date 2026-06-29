"""Context Cache — Phase 6.5.

Provides an optional, EventBus-integrated cache for EnterpriseContext assembly results.
Cache is feature-flagged (disabled by default) and never bypasses the EventBus.

Implementations:
  - MemoryContextCache: In-process dict-backed (M4 default)
  - RedisContextCache:  Stub — raises NotImplementedError (M5+)
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple

import structlog

from app.intelligence.intake.situation.enterprise_context import EnterpriseContext
from app.services.context_freshness import ContextFreshnessPolicy

logger = structlog.get_logger(__name__)


class AbstractContextCache(ABC):
    """Abstract interface for context caching."""

    @abstractmethod
    async def get(self, cache_key: str) -> Optional[EnterpriseContext]:
        """Retrieve a cached EnterpriseContext by key, or None if missing/expired."""
        pass

    @abstractmethod
    async def set(
        self,
        cache_key: str,
        context: EnterpriseContext,
        ttl_seconds: int,
    ) -> None:
        """Store an EnterpriseContext with a TTL."""
        pass

    @abstractmethod
    async def invalidate(
        self,
        cache_key: str,
        twin_id,
        reason: str = "manual_invalidation",
        event_bus=None,
    ) -> None:
        """Remove a cache entry and publish ContextInvalidatedEvent on the EventBus."""
        pass

    @abstractmethod
    async def is_fresh(
        self,
        cache_key: str,
        freshness_policy: ContextFreshnessPolicy,
    ) -> bool:
        """Return True if the cached entry satisfies the given freshness policy."""
        pass


class MemoryContextCache(AbstractContextCache):
    """In-process dictionary-backed cache (M4 default).

    Cache key pattern: "{twin_id}:{policy_id}:{intent_id or 'no_intent'}"
    Stores (EnterpriseContext, retrieved_at, expires_at) tuples.
    """

    def __init__(self) -> None:
        # {cache_key: (context, retrieved_at, expires_at)}
        self._store: Dict[str, Tuple[EnterpriseContext, datetime, datetime]] = {}

    async def get(self, cache_key: str) -> Optional[EnterpriseContext]:
        entry = self._store.get(cache_key)
        if entry is None:
            return None
        context, retrieved_at, expires_at = entry
        now = datetime.now(timezone.utc)
        if now > expires_at:
            del self._store[cache_key]
            logger.debug("Cache entry expired", cache_key=cache_key)
            return None
        return context

    async def set(
        self,
        cache_key: str,
        context: EnterpriseContext,
        ttl_seconds: int,
    ) -> None:
        from datetime import timedelta

        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=ttl_seconds)
        self._store[cache_key] = (context, now, expires_at)
        logger.debug(
            "Context cached",
            cache_key=cache_key,
            ttl_seconds=ttl_seconds,
        )

    async def invalidate(
        self,
        cache_key: str,
        twin_id,
        reason: str = "manual_invalidation",
        event_bus=None,
    ) -> None:
        removed = self._store.pop(cache_key, None)
        if removed:
            logger.info("Cache entry invalidated", cache_key=cache_key, reason=reason)
        if event_bus is not None:
            try:
                from app.shared.events.models import ContextInvalidatedEvent

                event = ContextInvalidatedEvent(
                    correlation_id=cache_key,
                    cache_key=cache_key,
                    twin_id=twin_id,
                    reason=reason,
                )
                event_bus.publish(event)
            except Exception as exc:
                logger.warning(
                    "Failed to publish ContextInvalidatedEvent", error=str(exc)
                )

    async def is_fresh(
        self,
        cache_key: str,
        freshness_policy: ContextFreshnessPolicy,
    ) -> bool:
        entry = self._store.get(cache_key)
        if entry is None:
            return False
        _, retrieved_at, _ = entry
        return not freshness_policy.is_stale(retrieved_at)

    def size(self) -> int:
        return len(self._store)

    def health(self) -> dict:
        return {"memory_context_cache": "ok", "entries": self.size()}


class RedisContextCache(AbstractContextCache):
    """Redis-backed cache stub. Raises NotImplementedError until M5.

    Designed for distributed deployment scenarios.
    """

    async def get(self, cache_key: str) -> Optional[EnterpriseContext]:
        raise NotImplementedError(
            "RedisContextCache is not implemented in Milestone 4."
        )

    async def set(
        self, cache_key: str, context: EnterpriseContext, ttl_seconds: int
    ) -> None:
        raise NotImplementedError(
            "RedisContextCache is not implemented in Milestone 4."
        )

    async def invalidate(
        self,
        cache_key: str,
        twin_id,
        reason: str = "manual_invalidation",
        event_bus=None,
    ) -> None:
        raise NotImplementedError(
            "RedisContextCache is not implemented in Milestone 4."
        )

    async def is_fresh(
        self, cache_key: str, freshness_policy: ContextFreshnessPolicy
    ) -> bool:
        raise NotImplementedError(
            "RedisContextCache is not implemented in Milestone 4."
        )


@staticmethod
def build_cache_key(twin_id, policy_id: str, intent_id=None) -> str:
    """Canonical cache key factory."""
    intent_part = str(intent_id) if intent_id else "no_intent"
    return f"{twin_id}:{policy_id}:{intent_part}"
