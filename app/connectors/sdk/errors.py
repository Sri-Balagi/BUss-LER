"""BizOS Structured Connector Error Model

Shields the BizOS kernel from raw provider-specific exceptions.
Converts all upstream failures (Google, Stripe, Razorpay) into standard ConnectorErrors.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ConnectorError(BaseModel):
    """Standardized error object returned by all connectors."""
    code: str  # e.g., AUTH_EXPIRED, RATE_LIMITED, INVALID_PARAMS, NETWORK_ERROR, PERMISSION_DENIED
    provider: str
    action: str
    severity: str = "ERROR"  # WARNING, ERROR, CRITICAL
    retryable: bool = False
    user_message: str
    technical_details: Dict[str, Any] = Field(default_factory=dict)


class ConnectorException(Exception):
    """Exception wrapping a structured ConnectorError."""

    def __init__(self, error: ConnectorError):
        self.error = error
        super().__init__(f"[{error.provider}:{error.action}] {error.code} - {error.user_message}")
