from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum


@dataclass(frozen=True)
class ExecutionContext:
    """
    An immutable record of the authenticated state for a given execution boundary.
    This context is propagated down the stack (Authentication -> Authorization -> Execution -> Audit).
    """

    # Core Identity Attributes
    is_authenticated: bool = False
    tenant_id: str | None = None
    user_id: str | None = None
    api_key_id: str | None = None

    # Authorization Attributes (populated by Authorization Service later, but tracked here)
    roles: list[str] = field(default_factory=list)
    scopes: list[str] = field(default_factory=list)

    # Observability & Traceability Metadata
    request_id: str | None = None
    correlation_id: str | None = None
    trace_id: str | None = None
    session_id: str | None = None

    # Authentication Context
    authentication_method: str | None = None
    authenticated_at: datetime | None = None

    @classmethod
    def anonymous(cls) -> "ExecutionContext":
        """Creates an anonymous execution context (unauthenticated)."""
        return cls(is_authenticated=False)


class AuthenticationStatus(StrEnum):
    SUCCESS = "SUCCESS"
    NO_CREDENTIALS = "NO_CREDENTIALS"
    INVALID_TOKEN = "INVALID_TOKEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    REVOKED = "REVOKED"
    UNSUPPORTED_SCHEME = "UNSUPPORTED_SCHEME"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"


@dataclass(frozen=True)
class AuthenticationResult:
    """
    An immutable value object representing the outcome of an authentication attempt.
    """
    status: AuthenticationStatus
    message: str
    context: ExecutionContext | None = None

    @classmethod
    def success(cls, context: ExecutionContext) -> "AuthenticationResult":
        return cls(status=AuthenticationStatus.SUCCESS, message="Authentication successful", context=context)

    @classmethod
    def failure(cls, status: AuthenticationStatus, message: str) -> "AuthenticationResult":
        return cls(status=status, message=message, context=None)


class DecisionSource(StrEnum):
    ROLE = "ROLE"
    DIRECT_PERMISSION = "DIRECT_PERMISSION"
    POLICY = "POLICY"
    DEFAULT_DENY = "DEFAULT_DENY"


@dataclass(frozen=True)
class AuthorizationDecision:
    """
    Structured metadata representing the outcome of an authorization evaluation.
    Includes details for future auditing and observability.
    """
    is_allowed: bool
    reason: str
    required_permission: str
    matched_permissions: list[str]
    decision_source: DecisionSource
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Optional metadata for detailed auditing and observability
    evaluated_roles: list[str] | None = None
    evaluated_permissions: list[str] | None = None
    matched_policy: str | None = None
    evaluation_duration_ms: float | None = None

    @classmethod
    def allow(
        cls,
        required_permission: str,
        matched_permissions: list[str],
        source: DecisionSource,
        reason: str = "Access granted",
        evaluated_roles: list[str] | None = None,
        evaluated_permissions: list[str] | None = None,
        matched_policy: str | None = None,
        evaluation_duration_ms: float | None = None
    ) -> "AuthorizationDecision":
        return cls(
            is_allowed=True,
            reason=reason,
            required_permission=required_permission,
            matched_permissions=matched_permissions,
            decision_source=source,
            evaluated_roles=evaluated_roles,
            evaluated_permissions=evaluated_permissions,
            matched_policy=matched_policy,
            evaluation_duration_ms=evaluation_duration_ms
        )

    @classmethod
    def deny(
        cls,
        required_permission: str,
        reason: str = "Access denied",
        source: DecisionSource = DecisionSource.DEFAULT_DENY,
        evaluated_roles: list[str] | None = None,
        evaluated_permissions: list[str] | None = None,
        matched_policy: str | None = None,
        evaluation_duration_ms: float | None = None
    ) -> "AuthorizationDecision":
        return cls(
            is_allowed=False,
            reason=reason,
            required_permission=required_permission,
            matched_permissions=[],
            decision_source=source,
            evaluated_roles=evaluated_roles,
            evaluated_permissions=evaluated_permissions,
            matched_policy=matched_policy,
            evaluation_duration_ms=evaluation_duration_ms
        )

@dataclass(frozen=True)
class SandboxPolicy:
    """
    Immutable model describing capabilities and constraints for a sandboxed execution.
    """
    allowed_directories: list[str] = field(default_factory=list)
    allow_network: bool = False
    allow_subprocess: bool = False
    allow_environment_variables: bool = False

    # Resource constraints
    max_execution_time_seconds: int | None = None
    max_memory_mb: int | None = None
    max_output_size_kb: int | None = None
