"""
Connector SDK — Base Interfaces.

Every connector in BizOS must subclass ``BaseConnector`` and implement
the abstract lifecycle methods. The SDK enforces a consistent contract
so the ConnectorManager can operate any connector without knowing its
implementation details.

Lifecycle States::

    INSTALLED → CONFIGURED → CONNECTED → ACTIVE → DEGRADED
        ↓                                              ↓
    UNINSTALLED                              SUSPENDED / DISCONNECTED
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Status & Capability Enums
# ---------------------------------------------------------------------------


class ConnectorStatus(StrEnum):
    """Runtime lifecycle status of a connector instance."""

    INSTALLED = "INSTALLED"
    CONFIGURED = "CONFIGURED"
    CONNECTED = "CONNECTED"
    ACTIVE = "ACTIVE"
    DEGRADED = "DEGRADED"
    DISCONNECTED = "DISCONNECTED"
    SUSPENDED = "SUSPENDED"
    UNINSTALLED = "UNINSTALLED"
    ERROR = "ERROR"


class AuthType(StrEnum):
    """Authentication mechanism used by a connector."""

    OAUTH2 = "oauth2"
    OAUTH2_PKCE = "oauth2_pkce"
    API_KEY = "api_key"
    JWT = "jwt"
    BASIC = "basic"
    SERVICE_ACCOUNT = "service_account"
    NONE = "none"


class SyncType(StrEnum):
    """Synchronization strategy."""

    FULL = "full"
    INCREMENTAL = "incremental"
    REAL_TIME = "real_time"
    MANUAL = "manual"
    SCHEDULED = "scheduled"


# ---------------------------------------------------------------------------
# Result Models
# ---------------------------------------------------------------------------


class ConnectorHealthResult(BaseModel):
    """Result of a connector health check."""

    connector_id: str
    profile_id: str | None = None
    healthy: bool
    status: ConnectorStatus
    latency_ms: float | None = None
    last_checked: datetime = Field(default_factory=lambda: datetime.now(UTC))
    message: str = ""
    details: dict[str, Any] = Field(default_factory=dict)


class SyncResult(BaseModel):
    """Result of a sync operation."""

    connector_id: str
    profile_id: str | None = None
    sync_type: SyncType
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    records_processed: int = 0
    records_created: int = 0
    records_updated: int = 0
    records_failed: int = 0
    cursor: str | None = None
    success: bool = False
    error: str | None = None


class WebhookResult(BaseModel):
    """Result of processing a webhook payload."""

    connector_id: str
    event_type: str
    processed: bool
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    error: str | None = None


class ValidationResult(BaseModel):
    """Result of connector validation check."""

    valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)
        self.valid = False

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)


# ---------------------------------------------------------------------------
# Base Connector
# ---------------------------------------------------------------------------


class BaseConnector(ABC):
    """
    Abstract base class for all BizOS connectors.

    Every connector must:
    1. Implement all abstract lifecycle methods.
    2. Declare its capabilities via ``get_capabilities()``.
    3. Use the SDK mixins (``SyncMixin``, ``HealthCheckMixin``, etc.) where
       applicable rather than reimplementing common behavior.

    The ConnectorManager interacts exclusively through this interface.
    """

    def __init__(
        self,
        connector_id: str,
        profile_id: str | None = None,
    ) -> None:
        self._connector_id = connector_id
        self._profile_id = profile_id or "default"
        self._status = ConnectorStatus.INSTALLED
        self._installed_at: datetime | None = None
        self._connected_at: datetime | None = None
        self._last_sync_at: datetime | None = None
        self._error: str | None = None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def connector_id(self) -> str:
        return self._connector_id

    @property
    def profile_id(self) -> str:
        return self._profile_id

    @property
    def status(self) -> ConnectorStatus:
        return self._status

    @property
    def is_active(self) -> bool:
        return self._status == ConnectorStatus.ACTIVE

    @property
    def is_connected(self) -> bool:
        return self._status in (ConnectorStatus.CONNECTED, ConnectorStatus.ACTIVE)

    # ------------------------------------------------------------------
    # Lifecycle — must be implemented by every connector
    # ------------------------------------------------------------------

    @abstractmethod
    async def install(self) -> None:
        """
        Called once when the connector is first installed.
        Use to register webhooks, initialize state, create subscriptions.
        """

    @abstractmethod
    async def uninstall(self) -> None:
        """
        Called when the connector is removed.
        Use to deregister webhooks, cleanup subscriptions, purge state.
        """

    @abstractmethod
    async def connect(self) -> None:
        """
        Establish a live connection to the external service.
        Called after ``authenticate()`` completes successfully.
        """

    @abstractmethod
    async def disconnect(self) -> None:
        """Gracefully sever the connection to the external service."""

    @abstractmethod
    async def authenticate(self) -> None:
        """
        Perform authentication with the external service.
        Stores credentials via the SecretVault.
        """

    @abstractmethod
    async def refresh_token(self) -> None:
        """Refresh OAuth tokens or re-authenticate. Called by the Scheduler."""

    @abstractmethod
    async def validate(self) -> ValidationResult:
        """Validate the connector's configuration and credential state."""

    @abstractmethod
    async def health_check(self) -> ConnectorHealthResult:
        """
        Check the connector's health.
        Must return quickly (target < 2s).
        """

    @abstractmethod
    async def sync(self, sync_type: SyncType = SyncType.INCREMENTAL) -> SyncResult:
        """
        Perform a data synchronization.
        Result must update cursor/checkpoint via the StateStore.
        """

    @abstractmethod
    async def handle_webhook(self, payload: dict[str, Any]) -> WebhookResult:
        """
        Handle an inbound webhook payload.
        The platform routes verified payloads here after signature checks.
        """

    @abstractmethod
    async def shutdown(self) -> None:
        """Called on graceful platform shutdown. Release resources."""

    # ------------------------------------------------------------------
    # Capabilities — must be declared by every connector
    # ------------------------------------------------------------------

    @abstractmethod
    def get_capabilities(self) -> list[str]:
        """
        Return the list of capability IDs this connector provides.
        Example: ["github.issue_management", "github.repository_management"]
        """

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _set_status(self, status: ConnectorStatus) -> None:
        self._status = status

    def _set_error(self, error: str | None) -> None:
        self._error = error
        if error:
            self._status = ConnectorStatus.ERROR

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"connector_id={self._connector_id!r}, "
            f"profile_id={self._profile_id!r}, "
            f"status={self._status!r})"
        )
