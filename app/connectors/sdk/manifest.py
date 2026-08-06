"""BizOS Connector Manifest Schema — Phase 2 Production Grade

Serves as the static source of truth for CLI, Studio, Planner Agents, HTTP API,
and documentation generators. Machine-readable, versioned, and JSON-serializable.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field

from app.connectors.sdk.permissions import ConnectorPermission


class ConnectorComplianceLevel(str, Enum):
    """Certification and compliance level for connectors."""
    EXPERIMENTAL = "EXPERIMENTAL"
    BETA = "BETA"
    CERTIFIED = "CERTIFIED"
    ENTERPRISE_CERTIFIED = "ENTERPRISE_CERTIFIED"


class RateLimitConfig(BaseModel):
    """Rate limit specification per connector."""
    requests_per_second: Optional[int] = None
    requests_per_minute: Optional[int] = None
    requests_per_hour: Optional[int] = None
    requests_per_day: Optional[int] = None
    concurrent_requests: Optional[int] = None
    upload_bytes_per_second: Optional[int] = None


class ConnectorManifest(BaseModel):
    """Declarative static manifest for a connector — machine-readable and JSON-serializable.

    This is the authoritative source of truth for:
    - CLI tooling (bizos connector inspect <id>)
    - BizOS Studio capability browser
    - Planner Agent dynamic workflow composition
    - Health monitoring and SLA tracking
    - SDK version compatibility checks
    """
    # ── Identity ─────────────────────────────────────────────────────────────
    connector_id: str
    display_name: str
    version: str = "4.0.0"
    sdk_version_compatibility: str = ">=4.0.0"
    provider: str
    description: str
    compliance_level: ConnectorComplianceLevel = ConnectorComplianceLevel.ENTERPRISE_CERTIFIED
    family: str = "general"
    parent_connector_id: Optional[str] = None
    documentation_url: Optional[str] = None

    # ── Capabilities ──────────────────────────────────────────────────────────
    capabilities: List[str] = Field(default_factory=list)
    supported_resources: List[str] = Field(default_factory=list)
    supported_events: List[str] = Field(default_factory=list)

    # ── Auth ─────────────────────────────────────────────────────────────────
    authentication_methods: List[str] = Field(default_factory=lambda: ["oauth2"])
    auth_type: str = "oauth2"
    required_scopes: List[str] = Field(default_factory=list)
    permissions: List[ConnectorPermission] = Field(default_factory=list)
    required_env_vars: List[str] = Field(default_factory=list)

    # ── Rate Limits ───────────────────────────────────────────────────────────
    rate_limits: RateLimitConfig = Field(default_factory=RateLimitConfig)

    # ── Feature Flags ─────────────────────────────────────────────────────────
    feature_flags: Dict[str, bool] = Field(default_factory=dict)

    # ── Config Schema (JSON Schema for connector config) ──────────────────────
    config_schema: Dict[str, Any] = Field(default_factory=dict)

    # ── Execution ─────────────────────────────────────────────────────────────
    supported_execution_modes: List[str] = Field(
        default_factory=lambda: ["SIMULATION", "DRY_RUN", "PRODUCTION"]
    )
    webhook_support: bool = False
    multi_account_support: bool = True
    supports_delta_sync: bool = False
    supports_streaming: bool = False
    supports_batch: bool = True
    supports_provider_sandbox: bool = False

    def to_json_schema(self) -> Dict[str, Any]:
        """Serialize manifest to JSON-compatible dict for API responses and CLI output."""
        return self.model_dump(mode="json")
