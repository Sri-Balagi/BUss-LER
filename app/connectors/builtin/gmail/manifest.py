"""Gmail Reference Connector Manifest."""
from app.connectors.registry.manifest import (
    ConnectorManifest, CapabilityDeclaration, AIMetadata,
    MarketplaceMetadata, PublisherInfo, ConnectorCategory, AuthType, SyncType
)

MANIFEST = ConnectorManifest(
    id="gmail",
    name="Gmail Connector",
    version="1.0.0",
    description="Google Gmail integration for email synchronization and notification monitoring.",
    author="BizOS Core Team",
    auth_type=AuthType.OAUTH2_PKCE,
    scopes=["https://www.googleapis.com/auth/gmail.readonly"],
    capabilities=[
        CapabilityDeclaration(
            capability_id="gmail.email_sync",
            name="Email Sync",
            description="Sync and retrieve user emails",
            operations=["list_messages", "get_message"],
            canonical_model="CanonicalEmail",
        ),
    ],
    supported_events=["EmailReceivedEvent"],
    supported_sync_types=[SyncType.FULL, SyncType.INCREMENTAL],
    supports_polling=True,
    ai_metadata=AIMetadata(
        description="Integrates Google Gmail messages and threads.",
        business_vocabulary=["email", "message", "inbox", "sender"],
        natural_language_aliases=["Gmail", "Google Mail", "email account"],
        supported_operations=["list_messages"],
    ),
    marketplace=MarketplaceMetadata(
        publisher=PublisherInfo(name="BizOS Core", website="https://bizos.ai", verified=True),
        category=ConnectorCategory.COMMUNICATION,
        tags=["email", "google", "mail"],
        pricing="free",
    ),
)
