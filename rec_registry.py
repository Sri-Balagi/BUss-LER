"""Context Provider Registry — Extension B.

Single point of provider registration, discovery, and capability lookup.
The ContextEngine never constructs providers directly — it obtains them here.

Future integrations (CRM, ERP, Slack, Email, Calendar, Inventory) register
themselves without requiring any modification to ContextEngine.
"""

from typing import Dict, List, Optional

from app.models.enterprise_context import ProviderMetadata
from app.models.enums import ContextSource
from app.models.exceptions import ProviderNotRegisteredError
from app.services.context_freshness import (
    ContextFreshnessPolicy,
    DEFAULT_FRESHNESS_POLICIES,
)
from app.services.context_retry import ProviderRetryConfig

import structlog

logger = structlog.get_logger(__name__)


class RegistrationEntry:
    """Internal registry entry holding provider + metadata + config."""

    def __init__(
        self,
        provider,  # AbstractContextProvider (typed at runtime)
        metadata: ProviderMetadata,
        freshness_policy: ContextFreshnessPolicy,
        retry_config: ProviderRetryConfig,
    ) -> None:
        self.provider = provider
        self.metadata = metadata
        self.freshness_policy = freshness_policy
        self.retry_config = retry_config


class ContextProviderRegistry:
    """Registry for all context providers.

    Responsibilities:
    - Register providers by ContextSource identifier
    - Discover registered providers
    - Expose capability lookup
    - Store per-provider metadata, freshness policy, retry config
    - Support plugin registration for future integrations
    """

    def __init__(self) -> None:
        self._registry: Dict[ContextSource, RegistrationEntry] = {}

    def register(
        self,
        provider,
        metadata: ProviderMetadata,
        freshness_policy: Optional[ContextFreshnessPolicy] = None,
        retry_config: Optional[ProviderRetryConfig] = None,
    ) -> None:
        """Register a provider for the given ContextSource.

        Args:
            provider:         An AbstractContextProvider instance.
            metadata:         ProviderMetadata describing the provider.
            freshness_policy: Optional freshness policy (defaults to DEFAULT_FRESHNESS_POLICIES).
            retry_config:     Optional retry config (defaults to ProviderRetryConfig defaults).
        """
        source = metadata.source
        if source in self._registry:
            logger.warning(
                "ContextProvider already registered — overwriting",
                source=source.value,
                previous=self._registry[source].metadata.name,
                new=metadata.name,
            )

        fp = freshness_policy or DEFAULT_FRESHNESS_POLICIES.get(
            source,
            ContextFreshnessPolicy(provider=source),
        )
        rc = retry_config or ProviderRetryConfig()

        self._registry[source] = RegistrationEntry(
            provider=provider,
            metadata=metadata,
            freshness_policy=fp,
            retry_config=rc,
        )
        logger.info(
            "ContextProvider registered",
            source=source.value,
            name=metadata.name,
            version=metadata.version,
        )

    def get(self, source: ContextSource):
        """Retrieve a registered provider by source.

        Raises:
            ProviderNotRegisteredError: If no provider is registered for the source.
        """
        entry = self._registry.get(source)
        if entry is None:
            raise ProviderNotRegisteredError(source.value)
        return entry.provider

    def get_entry(self, source: ContextSource) -> RegistrationEntry:
        """Retrieve the full registration entry (provider + config)."""
        entry = self._registry.get(source)
        if entry is None:
            raise ProviderNotRegisteredError(source.value)
        return entry

    def get_metadata(self, source: ContextSource) -> ProviderMetadata:
        return self.get_entry(source).metadata

    def get_freshness_policy(self, source: ContextSource) -> ContextFreshnessPolicy:
        return self.get_entry(source).freshness_policy

    def get_retry_config(self, source: ContextSource) -> ProviderRetryConfig:
        return self.get_entry(source).retry_config

    def is_registered(self, source: ContextSource) -> bool:
        return source in self._registry

    def registered_sources(self) -> List[ContextSource]:
        return list(self._registry.keys())

    def all_metadata(self) -> List[ProviderMetadata]:
        return [entry.metadata for entry in self._registry.values()]
