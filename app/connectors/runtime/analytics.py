"""BizOS Connector Analytics Tracker

Tracks request metrics, latencies, failure rates, token refreshes, and API quota usage.
Feeds directly into Prometheus and BizOS Metrics Service.
"""

import time
from typing import Any, Dict
from prometheus_client import Counter, Histogram

# Prometheus Metrics Definitions
CONNECTOR_REQUESTS = Counter(
    "bizos_connector_requests_total",
    "Total connector action execution requests",
    ["connector_id", "action", "status"],
)

CONNECTOR_LATENCY = Histogram(
    "bizos_connector_latency_seconds",
    "Connector action execution latency in seconds",
    ["connector_id", "action"],
)

CONNECTOR_TOKEN_REFRESHES = Counter(
    "bizos_connector_token_refreshes_total",
    "Total OAuth token refreshes executed",
    ["connector_id", "status"],
)


class ConnectorAnalyticsTracker:
    """Tracks real-time connector execution metrics."""

    _stats: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def record_execution(cls, connector_id: str, action: str, latency_seconds: float, success: bool):
        status_str = "success" if success else "failure"
        CONNECTOR_REQUESTS.labels(connector_id=connector_id, action=action, status=status_str).inc()
        CONNECTOR_LATENCY.labels(connector_id=connector_id, action=action).observe(latency_seconds)

        if connector_id not in cls._stats:
            cls._stats[connector_id] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "total_latency_seconds": 0.0,
                "token_refreshes": 0,
            }

        st = cls._stats[connector_id]
        st["total_requests"] += 1
        if success:
            st["successful_requests"] += 1
        else:
            st["failed_requests"] += 1
        st["total_latency_seconds"] += latency_seconds

    @classmethod
    def record_token_refresh(cls, connector_id: str, success: bool):
        status_str = "success" if success else "failure"
        CONNECTOR_TOKEN_REFRESHES.labels(connector_id=connector_id, status=status_str).inc()
        if connector_id in cls._stats:
            cls._stats[connector_id]["token_refreshes"] += 1

    @classmethod
    def get_connector_stats(cls, connector_id: str) -> Dict[str, Any]:
        st = cls._stats.get(connector_id, {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_latency_seconds": 0.0,
            "token_refreshes": 0,
        })
        tot = st["total_requests"]
        avg_lat = (st["total_latency_seconds"] / tot) if tot > 0 else 0.0
        success_rate = (st["successful_requests"] / tot * 100.0) if tot > 0 else 100.0

        return {
            "connector_id": connector_id,
            "total_requests": tot,
            "successful_requests": st["successful_requests"],
            "failed_requests": st["failed_requests"],
            "success_rate_pct": round(success_rate, 2),
            "average_latency_ms": round(avg_lat * 1000.0, 2),
            "token_refreshes": st["token_refreshes"],
        }
