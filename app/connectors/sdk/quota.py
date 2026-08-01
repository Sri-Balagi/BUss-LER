"""BizOS Provider Quota Monitoring & Rate Limit Tracker

Monitors API quotas (Google APIs, Stripe, Razorpay) and feeds quota metrics to Prometheus.
Exposes daily usage, remaining quota, consumption percentage, and rate-limit reset timestamps.
"""

from datetime import datetime, timezone
from typing import Any, Dict
from pydantic import BaseModel, Field
import structlog

logger = structlog.get_logger(__name__)


class ProviderQuotaStatus(BaseModel):
    """Quota and rate limit metrics for a connector provider."""
    connector_id: str
    daily_limit: int = 10000
    daily_usage: int = 0
    remaining_quota: int = 10000
    consumption_pct: float = 0.0
    reset_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ProviderQuotaTracker:
    """Central Quota Monitoring Registry."""

    _quotas: Dict[str, ProviderQuotaStatus] = {}

    @classmethod
    def record_api_call(cls, connector_id: str, cost: int = 1, daily_limit: int = 10000) -> ProviderQuotaStatus:
        if connector_id not in cls._quotas:
            cls._quotas[connector_id] = ProviderQuotaStatus(
                connector_id=connector_id,
                daily_limit=daily_limit,
                daily_usage=0,
                remaining_quota=daily_limit,
            )

        q = cls._quotas[connector_id]
        q.daily_usage += cost
        q.remaining_quota = max(0, q.daily_limit - q.daily_usage)
        q.consumption_pct = round((q.daily_usage / q.daily_limit) * 100.0, 2)

        if q.consumption_pct >= 90.0:
            logger.warning(
                "Connector approaching daily API quota limit",
                connector_id=connector_id,
                consumption_pct=q.consumption_pct,
            )

        return q

    @classmethod
    def get_quota_status(cls, connector_id: str) -> ProviderQuotaStatus:
        return cls._quotas.get(
            connector_id,
            ProviderQuotaStatus(connector_id=connector_id),
        )
