from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List
from enum import Enum

@dataclass(frozen=True)
class ExecutionContext:
    """
    An immutable record of the authenticated state for a given execution boundary.
    This context is propagated down the stack (Authentication -> Authorization -> Execution -> Audit).
    """
    
    # Core Identity Attributes
    is_authenticated: bool = False
    tenant_id: Optional[str] = None
    user_id: Optional[str] = None
    api_key_id: Optional[str] = None
    
    # Authorization Attributes (populated by Authorization Service later, but tracked here)
    roles: List[str] = field(default_factory=list)
    scopes: List[str] = field(default_factory=list)
    
    # Observability & Traceability Metadata
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None
    session_id: Optional[str] = None
    
    # Authentication Context
    authentication_method: Optional[str] = None
    authenticated_at: Optional[datetime] = None
    
    @classmethod
    def anonymous(cls) -> "ExecutionContext":
        """Creates an anonymous execution context (unauthenticated)."""
        return cls(is_authenticated=False)


class AuthenticationStatus(str, Enum):
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
    context: Optional[ExecutionContext] = None
    
    @classmethod
    def success(cls, context: ExecutionContext) -> "AuthenticationResult":
        return cls(status=AuthenticationStatus.SUCCESS, message="Authentication successful", context=context)
        
    @classmethod
    def failure(cls, status: AuthenticationStatus, message: str) -> "AuthenticationResult":
        return cls(status=status, message=message, context=None)


class DecisionSource(str, Enum):
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
    matched_permissions: List[str]
    decision_source: DecisionSource
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Optional metadata for detailed auditing and observability
    evaluated_roles: Optional[List[str]] = None
    evaluated_permissions: Optional[List[str]] = None
    matched_policy: Optional[str] = None
    evaluation_duration_ms: Optional[float] = None
    
    @classmethod
    def allow(
        cls, 
        required_permission: str, 
        matched_permissions: List[str], 
        source: DecisionSource, 
        reason: str = "Access granted",
        evaluated_roles: Optional[List[str]] = None,
        evaluated_permissions: Optional[List[str]] = None,
        matched_policy: Optional[str] = None,
        evaluation_duration_ms: Optional[float] = None
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
        evaluated_roles: Optional[List[str]] = None,
        evaluated_permissions: Optional[List[str]] = None,
        matched_policy: Optional[str] = None,
        evaluation_duration_ms: Optional[float] = None
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
    allowed_directories: List[str] = field(default_factory=list)
    allow_network: bool = False
    allow_subprocess: bool = False
    allow_environment_variables: bool = False
    
    # Resource constraints
    max_execution_time_seconds: Optional[int] = None
    max_memory_mb: Optional[int] = None
    max_output_size_kb: Optional[int] = None
