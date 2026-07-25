"""Signal Messaging Connector Architecture Stub."""
from app.connectors.registry.manifest import (
    ConnectorManifest, CapabilityDeclaration, AIMetadata,
    MarketplaceMetadata, PublisherInfo, ConnectorCategory, AuthType
)

MANIFEST = ConnectorManifest(
    id="signal",
    name="Signal Messaging Connector (Stub)",
    version="1.0.0",
    description="Architecture stub for Signal Private Messenger integration.",
    author="BizOS Core Team",
    auth_type=AuthType.NONE,
    capabilities=[
        CapabilityDeclaration(
            capability_id="signal.messaging",
            name="Signal Messaging",
            description="Send and receive end-to-end encrypted Signal messages",
            operations=["send_message"],
            canonical_model="CanonicalMessage",
        ),
    ],
    ai_metadata=AIMetadata(
        description="Architecture stub for Signal Private Messenger.",
        business_vocabulary=["signal", "encrypted", "chat"],
        natural_language_aliases=["Signal"],
    ),
    marketplace=MarketplaceMetadata(
        publisher=PublisherInfo(name="BizOS Core", website="https://bizos.ai", verified=True),
        category=ConnectorCategory.COMMUNICATION,
        tags=["signal", "privacy", "chat"],
    ),
)
