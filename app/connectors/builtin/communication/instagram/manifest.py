"""Instagram Messaging Manifest."""
from app.connectors.registry.manifest import (
    ConnectorManifest, CapabilityDeclaration, AIMetadata,
    MarketplaceMetadata, PublisherInfo, ConnectorCategory, AuthType, SyncType
)

MANIFEST = ConnectorManifest(
    id="instagram",
    name="Instagram Messaging Connector",
    version="1.0.0",
    description="Instagram Messaging API integration for Direct Messages.",
    author="BizOS Core Team",
    auth_type=AuthType.OAUTH2,
    scopes=["instagram_basic", "instagram_manage_messages"],
    capabilities=[
        CapabilityDeclaration(
            capability_id="instagram.messaging",
            name="Instagram Messaging",
            description="Send and receive Instagram Direct Messages",
            operations=["send_message", "reply_message"],
            canonical_model="CanonicalMessage",
            tool_ids=["instagram.send_message"],
        ),
    ],
    supported_events=["MessageReceivedEvent"],
    supported_sync_types=[SyncType.REAL_TIME],
    supports_webhooks=True,
    ai_metadata=AIMetadata(
        description="Integrates Instagram Direct Messages for business accounts.",
        business_vocabulary=["instagram", "dm", "direct message", "chat"],
        natural_language_aliases=["Instagram", "IG Direct"],
        supported_operations=["send_message"],
    ),
    marketplace=MarketplaceMetadata(
        publisher=PublisherInfo(name="BizOS Core", website="https://bizos.ai", verified=True),
        category=ConnectorCategory.COMMUNICATION,
        tags=["instagram", "dm", "social"],
        pricing="free",
    ),
)
