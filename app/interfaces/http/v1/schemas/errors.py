from enum import StrEnum


class ErrorCode(StrEnum):
    """
    Standardized, machine-readable error codes for the BizOS API.
    These codes are returned in the 'code' field of the ErrorDetail schema.
    """
    # Standard HTTP mapping
    BAD_REQUEST = "bad_request"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    NOT_FOUND = "not_found"
    METHOD_NOT_ALLOWED = "method_not_allowed"
    RATE_LIMITED = "rate_limited"
    INTERNAL_ERROR = "internal_error"
    SERVICE_UNAVAILABLE = "service_unavailable"

    # Validation & Context
    VALIDATION_ERROR = "validation_error"
    INVALID_STATE = "invalid_state"

    # Identity & Gateway Specific
    API_KEY_INVALID = "api_key_invalid"
    API_KEY_EXPIRED = "api_key_expired"
    API_KEY_REVOKED = "api_key_revoked"
    TENANT_SUSPENDED = "tenant_suspended"
    TENANT_NOT_FOUND = "tenant_not_found"

    # Execution & Limits
    QUOTA_EXCEEDED = "quota_exceeded"
    IDEMPOTENCY_CONFLICT = "idempotency_conflict"
    TIMEOUT = "timeout"
