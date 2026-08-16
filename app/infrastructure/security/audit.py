
import structlog

from app.domain.security.interfaces import IAuditPublisher, IAuditSink
from app.shared.events.bus import EventBus
from app.shared.events.models import AuditEvent

logger = structlog.get_logger(__name__)

class InMemoryAuditSink(IAuditSink):
    """
    In-memory sink for audit events. Useful for tests and local development.
    In future milestones, this will be replaced with PostgreSQL or SIEM sinks.
    """

    def __init__(self):
        self._events: list[AuditEvent] = []

    async def record(self, event: AuditEvent) -> None:
        self._events.append(event)
        logger.info("audit_event_recorded", event_id=str(event.event_id), category=event.category)

    def get_events(self) -> list[AuditEvent]:
        return list(self._events)

    def clear(self) -> None:
        self._events.clear()


class EventBusAuditPublisher(IAuditPublisher):
    """
    Publishes audit events using the domain EventBus.
    Provides decoupled asynchronous messaging for audit records.
    """

    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus

    def publish_audit(self, event: AuditEvent) -> None:
        """
        Publishes the audit event to the EventBus on a best-effort basis.
        """
        try:
            self._event_bus.publish(event)
        except Exception as e:
            # Audit publishing must be best-effort and never fail business operations.
            logger.error("audit_publish_failed", error=str(e), event_id=str(event.event_id))


class AuditSubscriber:
    """
    Subscribes to the EventBus for AuditEvents and routes them to an IAuditSink.
    """

    def __init__(self, event_bus: EventBus, sink: IAuditSink):
        self._sink = sink
        # Register for both generic AuditEvent and its subclass SecurityEvent
        # However, EventBus implementation might require strict type matching,
        # so we register the handler.
        event_bus.subscribe(AuditEvent, self._handle_audit_event)

        # We need to explicitly subscribe subclasses if the EventBus doesn't do inheritance matching
        from app.shared.events.models import SecurityEvent
        event_bus.subscribe(SecurityEvent, self._handle_audit_event)

    async def _handle_audit_event(self, event: AuditEvent) -> None:
        try:
            await self._sink.record(event)
        except Exception as e:
            logger.error("audit_sink_record_failed", error=str(e), event_id=str(event.event_id))
