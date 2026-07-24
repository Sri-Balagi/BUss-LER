import threading

from app.domain.intelligence.capability import CapabilityType
from app.domain.intelligence.provider import (
    ICapabilityRegistry,
    IIntelligenceProvider,
    ProviderLifecycleStatus,
)


class CapabilityRegistryService(ICapabilityRegistry):
    """
    Central registry for discovering and resolving intelligence capabilities.
    Supports hot-swapping and dynamic failover by checking ProviderLifecycleStatus.
    """

    def __init__(self):
        # Maps CapabilityType -> List of providers
        self._providers: dict[CapabilityType, list[IIntelligenceProvider]] = {}
        self._lock = threading.Lock()

    def register_provider(self, provider: IIntelligenceProvider) -> None:
        """Registers a new provider in the capability registry."""
        metadata = provider.get_metadata()
        with self._lock:
            if metadata.capability_type not in self._providers:
                self._providers[metadata.capability_type] = []

            # Avoid duplicate registrations
            existing = [p for p in self._providers[metadata.capability_type]
                        if p.get_metadata().capability_id == metadata.capability_id]
            if not existing:
                self._providers[metadata.capability_type].append(provider)

            # Keep sorted by priority descending
            self._providers[metadata.capability_type].sort(
                key=lambda p: p.get_metadata().priority, reverse=True
            )

    def resolve_provider(self, capability_type: CapabilityType, tags: list[str] | None = None) -> IIntelligenceProvider | None:
        """Resolves the highest-priority healthy provider."""
        with self._lock:
            candidates = self._providers.get(capability_type, [])

        # We want to prefer READY over DEGRADED, and higher priority over lower.
        # Filter out unavailable ones first.
        valid_candidates = []
        for provider in candidates:
            status = provider.get_status()
            if status in (ProviderLifecycleStatus.UNAVAILABLE, ProviderLifecycleStatus.INITIALIZING, ProviderLifecycleStatus.STOPPING):
                continue
            if tags:
                metadata = provider.get_metadata()
                if not all(tag in metadata.tags for tag in tags):
                    continue
            valid_candidates.append(provider)

        if not valid_candidates:
            return None

        # Sort valid candidates by (is_ready, priority) descending
        valid_candidates.sort(
            key=lambda p: (
                p.get_status() == ProviderLifecycleStatus.READY,
                p.get_metadata().priority
            ),
            reverse=True
        )
        return valid_candidates[0]

    def resolve_all_providers(self, capability_type: CapabilityType) -> list[IIntelligenceProvider]:
        """Resolves all healthy providers of the requested type."""
        with self._lock:
            candidates = self._providers.get(capability_type, [])

        healthy = []
        for provider in candidates:
            if provider.get_status() not in (ProviderLifecycleStatus.UNAVAILABLE, ProviderLifecycleStatus.INITIALIZING, ProviderLifecycleStatus.STOPPING):
                healthy.append(provider)
        return healthy
