import abc
import enum

from app.domain.intelligence.capability import CapabilityMetadata, CapabilityType


class ProviderLifecycleStatus(enum.StrEnum):
    INITIALIZING = "INITIALIZING"
    READY = "READY"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"
    STOPPING = "STOPPING"


class IIntelligenceProvider(abc.ABC):
    """Base interface for all pluggable intelligence providers."""

    @abc.abstractmethod
    def get_metadata(self) -> CapabilityMetadata:
        """Return the registration metadata for this provider."""
        pass

    @abc.abstractmethod
    def get_status(self) -> ProviderLifecycleStatus:
        """Return the real-time operational status of the provider."""
        pass


class ICapabilityRegistry(abc.ABC):
    """Dynamically registers and resolves intelligence capabilities."""

    @abc.abstractmethod
    def register_provider(self, provider: IIntelligenceProvider) -> None:
        pass

    @abc.abstractmethod
    def resolve_provider(self, capability_type: CapabilityType, tags: list[str] | None = None) -> IIntelligenceProvider | None:
        """Resolves the highest-priority healthy provider of the requested type."""
        pass

    @abc.abstractmethod
    def resolve_all_providers(self, capability_type: CapabilityType) -> list[IIntelligenceProvider]:
        """Resolves all healthy providers of the requested type (useful for ensembles)."""
        pass
