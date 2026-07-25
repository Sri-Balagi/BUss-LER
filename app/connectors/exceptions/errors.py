"""
Connector exception hierarchy.

All connector-specific errors extend from ``ConnectorError``.
Callers should catch specific subclasses; catch ``ConnectorError`` as a fallback.
"""

from __future__ import annotations


class ConnectorError(Exception):
    """Base exception for all connector platform errors."""

    def __init__(self, message: str, connector_id: str | None = None) -> None:
        super().__init__(message)
        self.connector_id = connector_id
        self.message = message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(connector_id={self.connector_id!r}, message={self.message!r})"


# ---------------------------------------------------------------------------
# Registry & Lifecycle
# ---------------------------------------------------------------------------


class ConnectorNotFoundError(ConnectorError):
    """Raised when a connector ID cannot be resolved in the registry."""


class ConnectorAlreadyRegisteredError(ConnectorError):
    """Raised when attempting to register a connector ID that already exists."""


class ConnectorNotInstalledError(ConnectorError):
    """Raised when an operation requires the connector to be installed first."""


class ConnectorAlreadyInstalledError(ConnectorError):
    """Raised when installing a connector that is already installed."""


class InvalidLifecycleTransitionError(ConnectorError):
    """Raised when a lifecycle state transition is not permitted."""

    def __init__(self, connector_id: str, from_state: str, to_state: str) -> None:
        super().__init__(
            f"Invalid transition {from_state!r} → {to_state!r}",
            connector_id=connector_id,
        )
        self.from_state = from_state
        self.to_state = to_state


class ConnectorLoadError(ConnectorError):
    """Raised when the ConnectorLoader cannot discover or import a connector package."""


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------


class AuthenticationError(ConnectorError):
    """Raised when authentication with the external service fails."""


class TokenExpiredError(AuthenticationError):
    """Raised when an OAuth access token has expired and cannot be refreshed."""


class TokenRefreshError(AuthenticationError):
    """Raised when a token refresh attempt fails."""


class InvalidCredentialsError(AuthenticationError):
    """Raised when the provided credentials are invalid."""


class InsufficientPermissionsError(AuthenticationError):
    """Raised when the authenticated account lacks required scopes or permissions."""


class OAuthFlowError(AuthenticationError):
    """Raised when an error occurs during the OAuth authorization flow."""


# ---------------------------------------------------------------------------
# Secret Management
# ---------------------------------------------------------------------------


class SecretError(ConnectorError):
    """Base exception for secret vault operations."""


class SecretNotFoundError(SecretError):
    """Raised when a secret key cannot be found in the vault."""


class SecretStorageError(SecretError):
    """Raised when a write to the secret vault fails."""


# ---------------------------------------------------------------------------
# Sync
# ---------------------------------------------------------------------------


class SyncError(ConnectorError):
    """Raised when a sync operation fails."""


class SyncConfigurationError(SyncError):
    """Raised when the connector is not properly configured for sync."""


class IncrementalSyncNotSupportedError(SyncError):
    """Raised when incremental sync is requested but not supported."""


# ---------------------------------------------------------------------------
# Webhook
# ---------------------------------------------------------------------------


class WebhookError(ConnectorError):
    """Base exception for webhook-related failures."""


class WebhookSignatureError(WebhookError):
    """Raised when webhook payload signature verification fails."""


class WebhookRegistrationError(WebhookError):
    """Raised when registering a webhook endpoint with the external service fails."""


class WebhookRoutingError(WebhookError):
    """Raised when an inbound webhook cannot be routed to a connector."""


# ---------------------------------------------------------------------------
# Rate Limiting
# ---------------------------------------------------------------------------


class RateLimitError(ConnectorError):
    """Raised when the connector is rate-limited by the external API."""

    def __init__(
        self,
        message: str,
        connector_id: str | None = None,
        retry_after: int | None = None,
    ) -> None:
        super().__init__(message, connector_id=connector_id)
        self.retry_after = retry_after  # seconds to wait before retrying


class QuotaExceededError(RateLimitError):
    """Raised when the API quota has been fully consumed for the current window."""


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


class ConfigurationError(ConnectorError):
    """Raised when the connector configuration is invalid or incomplete."""


class MissingConfigurationError(ConfigurationError):
    """Raised when a required configuration field is absent."""


# ---------------------------------------------------------------------------
# Canonical / Data Pipeline
# ---------------------------------------------------------------------------


class MappingError(ConnectorError):
    """Raised when a vendor object cannot be mapped to a canonical model."""


class TransformationError(ConnectorError):
    """Raised when the transformation pipeline fails to process a payload."""


class ValidationError(ConnectorError):
    """Raised when a vendor payload fails schema validation."""


# ---------------------------------------------------------------------------
# Retry
# ---------------------------------------------------------------------------


class RetryExhaustedError(ConnectorError):
    """Raised when all retry attempts are exhausted."""

    def __init__(
        self,
        message: str,
        connector_id: str | None = None,
        attempts: int = 0,
    ) -> None:
        super().__init__(message, connector_id=connector_id)
        self.attempts = attempts


class PermanentFailureError(ConnectorError):
    """Raised when the failure is classified as permanent (no retry should occur)."""


# ---------------------------------------------------------------------------
# Health & State
# ---------------------------------------------------------------------------


class HealthCheckError(ConnectorError):
    """Raised when a connector health check fails."""


class StateStoreError(ConnectorError):
    """Raised when reading or writing connector state fails."""


# ---------------------------------------------------------------------------
# Policy
# ---------------------------------------------------------------------------


class PolicyViolationError(ConnectorError):
    """Raised when an operation is blocked by an active connector policy."""

    def __init__(self, connector_id: str, policy: str, operation: str) -> None:
        super().__init__(
            f"Operation {operation!r} blocked by policy {policy!r}",
            connector_id=connector_id,
        )
        self.policy = policy
        self.operation = operation


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------


class ProfileNotFoundError(ConnectorError):
    """Raised when a connector profile cannot be found."""


class ProfileAlreadyExistsError(ConnectorError):
    """Raised when creating a profile that already exists."""


# ---------------------------------------------------------------------------
# Dependency
# ---------------------------------------------------------------------------


class DependencyNotSatisfiedError(ConnectorError):
    """Raised when a required connector dependency is not installed or active."""

    def __init__(self, connector_id: str, dependency_id: str) -> None:
        super().__init__(
            f"Required dependency {dependency_id!r} not satisfied",
            connector_id=connector_id,
        )
        self.dependency_id = dependency_id


# ---------------------------------------------------------------------------
# Tool Layer
# ---------------------------------------------------------------------------


class ToolNotFoundError(ConnectorError):
    """Raised when a connector tool cannot be resolved by the ToolRegistry."""


class ToolExecutionError(ConnectorError):
    """Raised when a connector tool invocation fails."""
