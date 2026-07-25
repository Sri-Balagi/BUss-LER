"""Discord Connector Manifest."""
from app.connectors.registry.manifest import (
    ConnectorManifest, CapabilityDeclaration, AIMetadata,
    MarketplaceMetadata, PublisherInfo, ConnectorCategory, AuthType, SyncType
)

MANIFEST = ConnectorManifest(
    id="discord",
    name="Discord Connector",
    version="1.0.0",
    description="Discord Bot API integration for server channels, threads, and direct messages.",
    author="BizOS Core Team",
    auth_type=AuthType.API_KEY,
    capabilities=[
        CapabilityDeclaration(
            capability_id="discord.messaging",
            name="Discord Messaging",
            description="Send messages and manage Discord server channels and threads",
            operations=["send_message", "reply_message"],
            canonical_model="CanonicalMessage",
            tool_ids=["discord.send_message"],
        ),
    ],
    supported_events=["MessageReceivedEvent"],
    supported_sync_types=[SyncType.REAL_TIME],
    supports_webhooks=True,
    ai_metadata=AIMetadata(
        description="Integrates Discord Bot API for server guild channels and threads.",
        business_vocabulary=["discord", "bot", "guild", "server", "channel"],
        natural_language_aliases=["Discord", "Discord Bot"],
        supported_operations=["send_message"],
    ),
    marketplace=MarketplaceMetadata(
        publisher=PublisherInfo(name="BizOS Core", website="https://bizos.ai", verified=True),
        category=ConnectorCategory.COMMUNICATION,
        tags=["discord", "bot", "chat"],
        pricing="free",
    ),
)
