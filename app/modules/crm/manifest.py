"""Manifest definition for CRM & Sales Pipeline Horizontal Business Module."""

from app.core.modules.models import (
    MarketplaceMetadata,
    ModuleCapabilities,
    ModuleCategory,
    ModuleManifest,
    ModuleType,
)

CRM_MANIFEST = ModuleManifest(
    module_id="bizos.modules.crm.v1",
    name="CRM & Sales Pipeline Management",
    description="Cross-industry Enterprise CRM Module for BizOS supporting Lead Management, Deals, Sales Pipelines, Customer Profiles, Activities, and AI Win Rate optimization.",
    version="1.0.0",
    module_type=ModuleType.HORIZONTAL,
    category=ModuleCategory.CRM,
    author="BizOS Core Engineering Team",
    dependencies=[],
    required_connectors=["email_smtp", "telephony_voip", "calendar_sync"],
    supported_languages=["en", "es", "fr"],
    supported_regions=["US", "EU", "GLOBAL"],
    capabilities=ModuleCapabilities(
        domain_entities=["Lead", "SalesOpportunity", "ContactPipeline", "ActivityLog", "CustomerSegment"],
        commands=["CreateLead", "QualifyOpportunity", "UpdateDealStage", "LogActivity"],
        queries=["GetActivePipeline", "GetCustomerProfile", "GetWinRateAnalytics"],
        events_published=["LeadCreated", "OpportunityWon", "OpportunityLost", "PipelineStageUpdated"],
        events_subscribed=["PaymentReceived", "CustomerCreated"],
        permissions=["crm:leads:manage", "crm:deals:manage", "crm:analytics:view"],
        ai_vocabularies=["Customer Lifetime Value", "Customer Acquisition Cost", "Pipeline Velocity"],
        provided_contracts=["ICustomerProvider"]
    ),
    marketplace=MarketplaceMetadata(
        publisher="BizOS Official",
        website="https://bizos.ai/modules/crm",
        support_email="crm-support@bizos.ai",
        license="Enterprise-Proprietary",
        min_bizos_version="1.0.0",
        price_model="subscription",
        tags=["crm", "sales", "leads", "pipeline", "deals", "customer"]
    ),
    configuration_schema={
        "default_currency": {"type": "string", "default": "USD"},
        "inactivity_alert_days": {"type": "integer", "default": 14},
        "target_win_rate_percent": {"type": "number", "default": 30.0}
    }
)
