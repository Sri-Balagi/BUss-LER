"""
Connector Manifest — the declarative descriptor for every BizOS connector.

Each connector package must provide a ``ConnectorManifest`` instance
(typically in ``manifest.py``) that the ``ConnectorLoader`` discovers
at startup. The manifest is the single source of truth for:

- Identity (id, name, version, author)
- Authentication type and required scopes
- Supported capabilities and events
- Configuration schema
- Dependency declarations
- Version compatibility rules
- AI metadata
- Marketplace metadata
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from app.connectors.sdk.base import AuthType, SyncType


# ---------------------------------------------------------------------------
# Supporting enumerations
# ---------------------------------------------------------------------------


class ConnectorCategory(StrEnum):
    """High-level category for marketplace and discovery."""

    COMMUNICATION = "communication"
    PRODUCTIVITY = "productivity"
    PROJECT_MANAGEMENT = "project_management"
    CRM = "crm"
    ERP = "erp"
    FINANCE = "finance"
    ECOMMERCE = "ecommerce"
    DEVTOOLS = "devtools"
    STORAGE = "storage"
    ANALYTICS = "analytics"
    SECURITY = "security"
    HR = "hr"
    MARKETING = "marketing"
    CUSTOM = "custom"


class ConnectorStability(StrEnum):
    EXPERIMENTAL = "experimental"
    BETA = "beta"
    STABLE = "stable"
    DEPRECATED = "deprecated"


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------


class ConnectorDependency(BaseModel):
    """Declares a dependency on another connector."""

    connector_id: str
    required: bool = False
    min_version: str | None = None
    reason: str = ""


class VersionCompatibility(BaseModel):
    """BizOS platform version requirements for this connector."""

    sdk_version: str = "2.0"
    min_bizos_version: str = "6.0.0"
    max_bizos_version: str | None = None
    migration_scripts: list[str] = Field(default_factory=list)
    breaking_changes: list[str] = Field(default_factory=list)
    deprecation_notices: list[str] = Field(default_factory=list)


class CapabilityDeclaration(BaseModel):
    """Declares a single capability exposed by the connector."""

    capability_id: str
    name: str
    description: str = ""
    operations: list[str] = Field(default_factory=list)
    canonical_model: str | None = None  # e.g. "CanonicalIssue"
    tool_ids: list[str] = Field(default_factory=list)


class ConfigFieldSchema(BaseModel):
    """Schema definition for a single configuration field."""

    name: str
    type: str  # "str", "int", "bool", "secret"
    description: str = ""
    required: bool = True
    default: Any = None
    env_var: str | None = None
    secret: bool = False
    choices: list[Any] = Field(default_factory=list)


class ConnectorConfigDeclaration(BaseModel):
    """Typed configuration schema declared in the manifest."""

    version: str = "1.0"
    fields: list[ConfigFieldSchema] = Field(default_factory=list)


class PublisherInfo(BaseModel):
    """Publisher metadata for marketplace display."""

    name: str
    website: str | None = None
    verified: bool = False
    support_url: str | None = None
    repository_url: str | None = None
    email: str | None = None


class MarketplaceMetadata(BaseModel):
    """Marketplace-facing metadata — future-proofed from day one."""

    publisher: PublisherInfo
    category: ConnectorCategory = ConnectorCategory.CUSTOM
    tags: list[str] = Field(default_factory=list)
    pricing: str = "free"  # "free", "freemium", "paid", "enterprise"
    documentation_url: str | None = None
    logo_url: str | None = None
    screenshots: list[str] = Field(default_factory=list)
    license: str = "MIT"
    website: str | None = None


class AIMetadata(BaseModel):
    """Metadata that helps BizOS AI Agents understand and reason about the connector."""

    description: str = ""
    business_vocabulary: list[str] = Field(default_factory=list)
    natural_language_aliases: list[str] = Field(default_factory=list)
    entity_definitions: dict[str, str] = Field(default_factory=dict)
    supported_operations: list[str] = Field(default_factory=list)
    usage_examples: list[str] = Field(default_factory=list)
    prompt_context: str = ""


class FeatureFlagDeclaration(BaseModel):
    """A feature flag declared in the connector manifest."""

    flag_id: str
    name: str
    default_enabled: bool = False
    description: str = ""


# ---------------------------------------------------------------------------
# Main Manifest
# ---------------------------------------------------------------------------


class ConnectorManifest(BaseModel):
    """
    Complete descriptor for a BizOS connector.

    This is the single source of truth for everything the platform needs to
    know about a connector at registration time.
    """

    # --- Identity ---
    id: str = Field(..., description="Unique connector identifier. e.g. 'github', 'gmail'")
    name: str = Field(..., description="Human-readable connector name.")
    version: str = Field(..., description="Semantic version. e.g. '1.2.0'")
    description: str = ""
    author: str = ""
    stability: ConnectorStability = ConnectorStability.STABLE

    # --- Authentication ---
    auth_type: AuthType = AuthType.OAUTH2
    scopes: list[str] = Field(default_factory=list)

    # --- Capabilities ---
    capabilities: list[CapabilityDeclaration] = Field(default_factory=list)

    # --- Events ---
    supported_events: list[str] = Field(
        default_factory=list,
        description="Domain event class names this connector may emit.",
    )

    # --- Sync ---
    supported_sync_types: list[SyncType] = Field(default_factory=list)
    supports_webhooks: bool = False
    supports_polling: bool = False

    # --- Configuration ---
    config_schema: ConnectorConfigDeclaration = Field(
        default_factory=ConnectorConfigDeclaration
    )

    # --- Dependencies ---
    dependencies: list[ConnectorDependency] = Field(default_factory=list)

    # --- Compatibility ---
    compatibility: VersionCompatibility = Field(default_factory=VersionCompatibility)

    # --- Feature Flags ---
    feature_flags: list[FeatureFlagDeclaration] = Field(default_factory=list)

    # --- AI Metadata ---
    ai_metadata: AIMetadata = Field(default_factory=AIMetadata)

    # --- Marketplace ---
    marketplace: MarketplaceMetadata | None = None

    # --- Runtime hints ---
    rate_limit_strategy: str = "token_bucket"
    max_retries: int = 3
    health_check_interval_seconds: int = 60
    sync_interval_seconds: int = 300

    @property
    def capability_ids(self) -> list[str]:
        return [c.capability_id for c in self.capabilities]

    def get_capability(self, capability_id: str) -> CapabilityDeclaration | None:
        for cap in self.capabilities:
            if cap.capability_id == capability_id:
                return cap
        return None

    def __repr__(self) -> str:
        return f"ConnectorManifest(id={self.id!r}, version={self.version!r})"
