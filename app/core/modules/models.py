"""Module Manifest, Metadata, Context, and Capabilities models."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ModuleType(str, Enum):
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    SYSTEM = "system"


class ModuleCategory(str, Enum):
    # Vertical Industry Categories
    RESTAURANT = "restaurant"
    COMMERCE = "commerce"
    HOSPITALITY = "hospitality"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    EDUCATION = "education"
    MANUFACTURING = "manufacturing"
    LOGISTICS = "logistics"
    CONSTRUCTION = "construction"
    AGRICULTURE = "agriculture"
    GOVERNMENT = "government"
    LEGAL = "legal"
    HUMAN_RESOURCES = "human_resources"
    INFORMATION_TECHNOLOGY = "information_technology"
    TELECOMMUNICATIONS = "telecommunications"
    MEDIA = "media"
    ENERGY = "energy"
    TRANSPORTATION = "transportation"
    REAL_ESTATE = "real_estate"
    BEAUTY_WELLNESS = "beauty_wellness"
    SPORTS = "sports"
    TRAVEL = "travel"
    NON_PROFIT = "non_profit"
    SECURITY = "security"
    SCIENTIFIC = "scientific"
    CREATIVE = "creative"
    MISCELLANEOUS = "miscellaneous"

    # Horizontal Functional Categories
    CRM = "crm"
    HRM = "hrm"
    ACCOUNTING = "accounting"
    OPERATIONS = "operations"
    PROJECT_MANAGEMENT = "project_management"
    KNOWLEDGE_CONTENT = "knowledge_content"
    COMMUNICATION = "communication"
    ANALYTICS = "analytics"
    GOVERNANCE = "governance"
    AI_AUTOMATION = "ai_automation"


class MarketplaceMetadata(BaseModel):
    """Metadata required for BizOS Marketplace publishing."""

    publisher: str = "BizOS Core"
    website: str = "https://bizos.ai"
    support_email: str = "support@bizos.ai"
    license: str = "Apache-2.0"
    min_bizos_version: str = "1.0.0"
    max_bizos_version: str | None = None
    price_model: str = "free"  # free, subscription, one_time
    tags: list[str] = Field(default_factory=list)


class ModuleCapabilities(BaseModel):
    """Declarative capability registry exposed by a module."""

    domain_entities: list[str] = Field(default_factory=list)
    commands: list[str] = Field(default_factory=list)
    queries: list[str] = Field(default_factory=list)
    events_published: list[str] = Field(default_factory=list)
    events_subscribed: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
    ai_vocabularies: list[str] = Field(default_factory=list)
    provided_contracts: list[str] = Field(default_factory=list)


class ModuleManifest(BaseModel):
    """Canonical Manifest schema exposed by every BizOS Module."""

    module_id: str
    name: str
    description: str
    version: str = "1.0.0"
    module_type: ModuleType = ModuleType.VERTICAL
    category: ModuleCategory = ModuleCategory.RESTAURANT
    author: str = "BizOS Team"
    dependencies: list[str] = Field(default_factory=list)  # e.g. ["bizos.modules.inventory.v1"]
    required_connectors: list[str] = Field(default_factory=list)
    supported_languages: list[str] = Field(default_factory=lambda: ["en"])
    supported_regions: list[str] = Field(default_factory=lambda: ["US", "GLOBAL"])
    capabilities: ModuleCapabilities = Field(default_factory=ModuleCapabilities)
    marketplace: MarketplaceMetadata = Field(default_factory=MarketplaceMetadata)
    configuration_schema: dict[str, Any] = Field(default_factory=dict)


class ModuleMetadata(BaseModel):
    """Runtime runtime metadata for loaded module instances."""

    manifest: ModuleManifest
    install_time: str
    status: str = "INSTALLED"
    is_enabled: bool = True
    config: dict[str, Any] = Field(default_factory=dict)


class ModuleConfiguration(BaseModel):
    """Runtime configuration container for a module."""

    module_id: str
    tenant_id: str
    settings: dict[str, Any] = Field(default_factory=dict)
    feature_flags: dict[str, bool] = Field(default_factory=dict)


class ModuleContext(BaseModel):
    """Context passed to a module during lifecycle execution."""

    tenant_id: str
    user_id: str | None = None
    correlation_id: str | None = None
    environment: str = "production"
    config: ModuleConfiguration | None = None
