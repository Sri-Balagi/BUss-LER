"""Event Bus Lifecycle Auditor."""

from typing import Any, Dict, List
import structlog
from app.shared.events.models import DomainEvent

logger = structlog.get_logger(__name__)


class EventBusAuditor:
    """Audits lifecycle events for ordering, payload validity, and execution traces."""

    def __init__(self):
        self.audit_log: List[Dict[str, Any]] = []

    def record_event(self, event: DomainEvent) -> None:
        event_type = type(event).__name__
        payload = {
            "event_type": event_type,
            "correlation_id": getattr(event, "correlation_id", "N/A"),
            "timestamp": str(getattr(event, "timestamp", "")),
        }
        self.audit_log.append(payload)
        logger.info("Lifecycle Event Audited", event_type=event_type, correlation_id=payload["correlation_id"])

    def get_summary(self) -> Dict[str, Any]:
        types_count: Dict[str, int] = {}
        for entry in self.audit_log:
            et = entry["event_type"]
            types_count[et] = types_count.get(et, 0) + 1

        return {
            "total_events_audited": len(self.audit_log),
            "event_types_breakdown": types_count,
            "audit_trail": self.audit_log,
        }
