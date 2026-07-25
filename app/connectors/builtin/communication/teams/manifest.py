"""Microsoft Teams Connector Manifest."""
from app.connectors.registry.manifest import (
    ConnectorManifest, CapabilityDeclaration, AIMetadata,
    MarketplaceMetadata, PublisherInfo, ConnectorCategory, AuthType, SyncType
)

MANIFEST = ConnectorManifest(
    id="teams",
    name="Microsoft Teams Connector",
    version="1.0.0",
    description="Microsoft Graph API integration for Teams channels, chats, and meetings.",
    author="BizOS Core Team",
    auth_type=AuthType.OAUTH2,
    scopes=["ChatMessage.Send", "ChannelMessage.Read.All"],
    capabilities=[
        CapabilityDeclaration(
            capability_id="teams.messaging",
            name="Teams Messaging",
            description="Send messages and manage Teams chat conversations",
            operations=["send_message", "reply_message"],
            canonical_model="CanonicalMessage",
            tool_ids=["teams.send_message"],
        ),
    ],
    supported_events=["MessageReceivedEvent"],
    supported_sync_types=[SyncType.REAL_TIME],
    supports_webhooks=True,
    ai_metadata=AIMetadata(
        description="Integrates Microsoft Teams chats and channel conversations.",
        business_vocabulary=["teams", "microsoft", "channel", "chat"],
        natural_language_aliases=["MS Teams", "Teams"],
        supported_operations=["send_message"],
    ),
    marketplace=MarketplaceMetadata(
        publisher=PublisherInfo(name="BizOS Core", website="https://bizos.ai", verified=True),
        category=ConnectorCategory.COMMUNICATION,
        tags=["teams", "microsoft", "chat"],
        pricing="free",
    ),
)
