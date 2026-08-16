"""BizOS Connector Manifest Schema

Serves as the static source of truth for CLI, Studio, Planner Agents, HTTP API, and documentation.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.connectors.sdk.permissions import ConnectorPermission


class ConnectorComplianceLevel(str, Enum):
    """Certification and compliance level for connectors."""
    EXPERIMENTAL = "EXPERIMENTAL"
    BETA = "BETA"
    CERTIFIED = "CERTIFIED"
    ENTERPRISE_CERTIFIED = "ENTERPRISE_CERTIFIED"


class ConnectorManifest(BaseModel):
    """Declarative static manifest for a connector family or provider."""
    connector_id: str
    display_name: str
    version: str = "1.0.0"
    provider: str
    description: str
    compliance_level: ConnectorComplianceLevel = ConnectorComplianceLevel.CERTIFIED
    family: str = "general"
    parent_connector_id: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)
    permissions: List[ConnectorPermission] = Field(default_factory=list)
    feature_flags: Dict[str, bool] = Field(
        default_factory=lambda: {
            "enable_send_email": True,
            "enable_read_email": True,
            "enable_calendar_write": True,
            "enable_financial_reports": True,
            "enable_live_payments": False,
        }
    )
    supported_execution_modes: List[str] = Field(
        default_factory=lambda: ["SIMULATION", "DRY_RUN", "PRODUCTION"]
    )
    auth_type: str = "oauth2"  # oauth2, api_key, jwt
    webhook_support: bool = False
    multi_account_support: bool = True
    supports_provider_sandbox: bool = True
    documentation_url: Optional[str] = None
