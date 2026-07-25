"""Outlook Mail Connector Manifest."""
from app.connectors.registry.manifest import (
    ConnectorManifest, CapabilityDeclaration, AIMetadata,
    MarketplaceMetadata, PublisherInfo, ConnectorCategory, AuthType, SyncType
)

MANIFEST = ConnectorManifest(
    id="outlook",
    name="Outlook Mail Connector",
    version="1.0.0",
    description="Microsoft Graph API integration for Outlook Email and Calendars.",
    author="BizOS Core Team",
    auth_type=AuthType.OAUTH2,
    scopes=["Mail.ReadWrite", "Mail.Send"],
    capabilities=[
        CapabilityDeclaration(
            capability_id="outlook.email_sync",
            name="Outlook Email Sync",
            description="Send, retrieve, and organize Outlook emails",
            operations=["send_email", "list_messages"],
            canonical_model="CanonicalEmail",
            tool_ids=["outlook.send_email"],
        ),
    ],
    supported_events=["EmailReceivedEvent"],
    supported_sync_types=[SyncType.FULL, SyncType.INCREMENTAL],
    supports_webhooks=True,
    ai_metadata=AIMetadata(
        description="Integrates Microsoft Outlook Email messages and folders.",
        business_vocabulary=["outlook", "email", "mail", "microsoft"],
        natural_language_aliases=["Outlook", "Outlook Mail", "Office365 Mail"],
        supported_operations=["send_email"],
    ),
    marketplace=MarketplaceMetadata(
        publisher=PublisherInfo(name="BizOS Core", website="https://bizos.ai", verified=True),
        category=ConnectorCategory.COMMUNICATION,
        tags=["outlook", "email", "microsoft"],
        pricing="free",
    ),
)
