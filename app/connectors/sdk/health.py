"""BizOS Rich Connector Health Model"""

from enum import Enum
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ConnectorHealthStatus(str, Enum):
    """Richer health states for monitoring, Studio, and CLI."""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    AUTHENTICATION_REQUIRED = "AUTHENTICATION_REQUIRED"
    RATE_LIMITED = "RATE_LIMITED"
    TOKEN_EXPIRING = "TOKEN_EXPIRING"
    PROVIDER_OUTAGE = "PROVIDER_OUTAGE"
    MAINTENANCE = "MAINTENANCE"
    DISABLED = "DISABLED"


class ConnectorHealthReport(BaseModel):
    """Detailed health report returned by connector health_check()."""
    connector_id: str
    version: str
    status: ConnectorHealthStatus
    message: str
    vault_configured: bool = False
    sandbox_mode: bool = False
    checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    details: Dict[str, Any] = Field(default_factory=dict)
