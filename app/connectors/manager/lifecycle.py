"""
Connector Lifecycle State Machine.

Enforces the formal state transitions for a connector instance.
Invalid transitions raise ``InvalidLifecycleTransitionError``.

State Diagram::

    ┌─────────────────────────────────────────────────────────────┐
    │                                                             │
    │  [INSTALLED] → [CONFIGURED] → [CONNECTED] → [ACTIVE]        │
    │       ↓              ↓              ↓           ↓           │
    │  [UNINSTALLED]   [ERROR]      [DEGRADED]  [SUSPENDED]       │
    │                                    ↓           ↓           │
    │                             [DISCONNECTED] ← ──┘           │
    │                                    ↓                       │
    │                             [UNINSTALLED]                  │
    │                                                             │
    └─────────────────────────────────────────────────────────────┘

Install Flow (expanded, #21)::

    INSTALL → VALIDATE → CONFIGURE → AUTHENTICATE → TEST → ENABLE → ACTIVATE
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from enum import StrEnum

from app.connectors.exceptions.errors import InvalidLifecycleTransitionError
from app.connectors.sdk.base import ConnectorStatus

logger = logging.getLogger(__name__)


class LifecyclePhase(StrEnum):
    """Fine-grained install phases (separate from ConnectorStatus)."""

    PENDING = "PENDING"
    VALIDATING = "VALIDATING"
    CONFIGURING = "CONFIGURING"
    AUTHENTICATING = "AUTHENTICATING"
    TESTING = "TESTING"
    ENABLING = "ENABLING"
    ACTIVE = "ACTIVE"
    FAILED = "FAILED"


# Allowed transitions: current_status → set of valid next statuses
_ALLOWED_TRANSITIONS: dict[ConnectorStatus, set[ConnectorStatus]] = {
    ConnectorStatus.INSTALLED: {
        ConnectorStatus.CONFIGURED,
        ConnectorStatus.ERROR,
        ConnectorStatus.UNINSTALLED,
    },
    ConnectorStatus.CONFIGURED: {
        ConnectorStatus.CONNECTED,
        ConnectorStatus.ERROR,
        ConnectorStatus.INSTALLED,
        ConnectorStatus.UNINSTALLED,
    },
    ConnectorStatus.CONNECTED: {
        ConnectorStatus.ACTIVE,
        ConnectorStatus.DEGRADED,
        ConnectorStatus.DISCONNECTED,
        ConnectorStatus.ERROR,
    },
    ConnectorStatus.ACTIVE: {
        ConnectorStatus.DEGRADED,
        ConnectorStatus.SUSPENDED,
        ConnectorStatus.DISCONNECTED,
        ConnectorStatus.ERROR,
    },
    ConnectorStatus.DEGRADED: {
        ConnectorStatus.ACTIVE,
        ConnectorStatus.DISCONNECTED,
        ConnectorStatus.ERROR,
    },
    ConnectorStatus.SUSPENDED: {
        ConnectorStatus.ACTIVE,
        ConnectorStatus.DISCONNECTED,
        ConnectorStatus.UNINSTALLED,
    },
    ConnectorStatus.DISCONNECTED: {
        ConnectorStatus.CONNECTED,
        ConnectorStatus.UNINSTALLED,
    },
    ConnectorStatus.ERROR: {
        ConnectorStatus.INSTALLED,
        ConnectorStatus.CONFIGURED,
        ConnectorStatus.UNINSTALLED,
    },
    ConnectorStatus.UNINSTALLED: set(),  # terminal
}


class ConnectorLifecycleRecord:
    """Tracks the lifecycle history of a single connector instance."""

    def __init__(self, connector_id: str, profile_id: str) -> None:
        self.connector_id = connector_id
        self.profile_id = profile_id
        self.current_status = ConnectorStatus.INSTALLED
        self.history: list[tuple[ConnectorStatus, datetime, str]] = [
            (ConnectorStatus.INSTALLED, datetime.now(UTC), "Initial install")
        ]
        self.error: str | None = None
        self.install_phase: LifecyclePhase = LifecyclePhase.PENDING

    def transition(self, new_status: ConnectorStatus, reason: str = "") -> None:
        """
        Apply a state transition.

        Args:
            new_status: The desired next status.
            reason: Human-readable reason for the transition.

        Raises:
            InvalidLifecycleTransitionError: If the transition is not permitted.
        """
        allowed = _ALLOWED_TRANSITIONS.get(self.current_status, set())
        if new_status not in allowed:
            raise InvalidLifecycleTransitionError(
                connector_id=self.connector_id,
                from_state=self.current_status.value,
                to_state=new_status.value,
            )

        prev = self.current_status
        self.current_status = new_status
        self.history.append((new_status, datetime.now(UTC), reason))

        if new_status == ConnectorStatus.ERROR:
            self.error = reason
        elif prev == ConnectorStatus.ERROR:
            self.error = None  # clear error on recovery

        logger.info(
            "Connector %s[%s] %s → %s (%s)",
            self.connector_id,
            self.profile_id,
            prev.value,
            new_status.value,
            reason or "—",
        )

    def can_transition(self, new_status: ConnectorStatus) -> bool:
        allowed = _ALLOWED_TRANSITIONS.get(self.current_status, set())
        return new_status in allowed

    @property
    def is_active(self) -> bool:
        return self.current_status == ConnectorStatus.ACTIVE

    @property
    def is_operational(self) -> bool:
        return self.current_status in (
            ConnectorStatus.CONNECTED,
            ConnectorStatus.ACTIVE,
            ConnectorStatus.DEGRADED,
        )

    @property
    def last_transition_at(self) -> datetime:
        return self.history[-1][1]

    def summary(self) -> dict[str, object]:
        return {
            "connector_id": self.connector_id,
            "profile_id": self.profile_id,
            "status": self.current_status.value,
            "error": self.error,
            "last_transition": self.last_transition_at.isoformat(),
            "history_length": len(self.history),
        }
