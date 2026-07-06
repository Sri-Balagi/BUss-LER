"""Context Provider Registry — Extension B.

Single point of provider registration, discovery, and capability lookup.
The ContextEngine never constructs providers directly — it obtains them here.

Future integrations (CRM, ERP, Slack, Email, Calendar, Inventory) register
themselves without requiring any modification to ContextEngine.
"""

from typing import Dict, List, Optional, Iterator

from app.intelligence.intake.situation.enterprise_context import ProviderMetadata
from app.shared.enums import ContextSource
from app.shared.exceptions.errors import ProviderNotRegisteredError, BizOSError
from app.application.context.foundation.context_freshness import (
    ContextFreshnessPolicy,
    DEFAULT_FRESHNESS_POLICIES,
)
from app.platform.resilience.context_retry import ProviderRetryConfig
from app.application.context.providers.abstract import AbstractContextProvider

import structlog

logger = structlog.get_logger(__name__)


class DuplicateProviderRegistrationError(BizOSError):
    """Raised when attempting to register a provider for a source that is already registered."""
    
    def __init__(self, source: ContextSource):
        super().__init__(
            message=f"A provider is already registered for source '{source.value}'.",
            detail="Silent replacement is not allowed. Unregister the existing provider first."
        )


class RegistrationEntry:
    """Internal registry entry holding provider + metadata + config."""

    def __init__(
        self,
        provider: AbstractContextProvider,
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
        provider: AbstractContextProvider,
        metadata: ProviderMetadata,
        freshness_policy: Optional[ContextFreshnessPolicy] = None,
        retry_config: Optional[ProviderRetryConfig] = None,
    ) -> None:
        """Register a provider for the given ContextSource.

        Raises:
            DuplicateProviderRegistrationError: If a provider is already registered for this source.
        """
        source = metadata.source
        if source in self._registry:
            raise DuplicateProviderRegistrationError(source)

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

    def unregister(self, source: ContextSource) -> None:
        """Unregister a provider by source.
        
        Raises:
            ProviderNotRegisteredError: If no provider is registered for the source.
        """
        if source not in self._registry:
            raise ProviderNotRegisteredError(source.value)
        
        del self._registry[source]
        logger.info("ContextProvider unregistered", source=source.value)

    def get(self, source: ContextSource) -> AbstractContextProvider:
        """Retrieve a registered provider by source.

        Raises:
            ProviderNotRegisteredError: If no provider is registered for the source.
        """
        return self.get_entry(source).provider

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

    def __contains__(self, source: ContextSource) -> bool:
        return self.is_registered(source)

    def __len__(self) -> int:
        return len(self._registry)

    def __iter__(self) -> Iterator[RegistrationEntry]:
        """Iterate over all registration entries deterministically (by source value)."""
        for source in sorted(self._registry.keys(), key=lambda s: s.value):
            yield self._registry[source]
