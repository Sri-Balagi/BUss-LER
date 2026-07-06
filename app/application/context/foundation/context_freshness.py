"""Context Freshness Policy — Extension D.

Each context provider declares a ContextFreshnessPolicy that governs
how long its contribution remains valid in the cache.

The cache layer uses these policies instead of relying solely on raw TTL values.
"""

from datetime import datetime, timedelta, timezone

from app.interfaces.http.schemas.base import DomainBaseModel
from app.shared.enums import ContextSource, RefreshStrategy


class ContextFreshnessPolicy(DomainBaseModel):
    """Freshness semantics for a single context provider's cached result.

    Attributes:
        provider:           The ContextSource this policy applies to.
        max_age_seconds:    Maximum age (in seconds) before the cached item is stale.
        cache_ttl_seconds:  How long the cache entry lives regardless of staleness.
        refresh_strategy:   How the cache should handle approaching expiry.
    """

    provider: ContextSource
    max_age_seconds: int = 300  # 5 minutes default
    cache_ttl_seconds: int = 600  # 10 minutes default TTL
    refresh_strategy: RefreshStrategy = RefreshStrategy.LAZY

    def is_stale(self, retrieved_at: datetime) -> bool:
        """Return True if the cached entry has exceeded its max_age."""
        age = (datetime.now(timezone.utc) - retrieved_at).total_seconds()
        return age > self.max_age_seconds

    def expires_at(self, retrieved_at: datetime) -> datetime:
        """Return the absolute datetime when the cache entry expires."""
        return retrieved_at + timedelta(seconds=self.cache_ttl_seconds)


# =============================================================================
# Default freshness policies per provider
# =============================================================================

DEFAULT_FRESHNESS_POLICIES: dict[ContextSource, ContextFreshnessPolicy] = {
    ContextSource.MEMORY: ContextFreshnessPolicy(
        provider=ContextSource.MEMORY,
        max_age_seconds=300,
        cache_ttl_seconds=600,
        refresh_strategy=RefreshStrategy.LAZY,
    ),
    ContextSource.INTENT: ContextFreshnessPolicy(
        provider=ContextSource.INTENT,
        max_age_seconds=60,  # Intent is very fresh — 1 minute max
        cache_ttl_seconds=120,
        refresh_strategy=RefreshStrategy.FORCED,  # Always re-fetch intent
    ),
    ContextSource.GOAL: ContextFreshnessPolicy(
        provider=ContextSource.GOAL,
        max_age_seconds=600,
        cache_ttl_seconds=1200,
        refresh_strategy=RefreshStrategy.LAZY,
    ),
    ContextSource.PLAN: ContextFreshnessPolicy(
        provider=ContextSource.PLAN,
        max_age_seconds=600,
        cache_ttl_seconds=1200,
        refresh_strategy=RefreshStrategy.LAZY,
    ),
    ContextSource.RECOMMENDATION: ContextFreshnessPolicy(
        provider=ContextSource.RECOMMENDATION,
        max_age_seconds=300,
        cache_ttl_seconds=600,
        refresh_strategy=RefreshStrategy.LAZY,
    ),
    ContextSource.TWIN: ContextFreshnessPolicy(
        provider=ContextSource.TWIN,
        max_age_seconds=120,
        cache_ttl_seconds=300,
        refresh_strategy=RefreshStrategy.EAGER,
    ),
    ContextSource.CONVERSATION: ContextFreshnessPolicy(
        provider=ContextSource.CONVERSATION,
        max_age_seconds=30,  # Conversation is highly dynamic
        cache_ttl_seconds=60,
        refresh_strategy=RefreshStrategy.FORCED,
    ),
    ContextSource.TRACE: ContextFreshnessPolicy(
        provider=ContextSource.TRACE,
        max_age_seconds=900,
        cache_ttl_seconds=1800,
        refresh_strategy=RefreshStrategy.LAZY,
    ),
    ContextSource.BUSINESS_STATE: ContextFreshnessPolicy(
        provider=ContextSource.BUSINESS_STATE,
        max_age_seconds=120,
        cache_ttl_seconds=300,
        refresh_strategy=RefreshStrategy.EAGER,
    ),
    ContextSource.EXTERNAL: ContextFreshnessPolicy(
        provider=ContextSource.EXTERNAL,
        max_age_seconds=1800,  # External integrations are slow — 30 min
        cache_ttl_seconds=3600,
        refresh_strategy=RefreshStrategy.LAZY,
    ),
}
