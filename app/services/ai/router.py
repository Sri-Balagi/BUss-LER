from typing import Optional

from app.services.ai.providers.base import AbstractAIProvider
from app.services.ai.registry import ProviderRegistry


class ProviderRouter:
    """
    Selects the active provider from the registry based on capability or configuration.
    """

    def __init__(self, registry: ProviderRegistry, default_provider: str = "gemini"):
        self._registry = registry
        self._default_provider = default_provider

    def get_active_provider(self, requested_provider: Optional[str] = None) -> AbstractAIProvider:
        """
        Return the requested provider, or the default if none is specified.
        In the future, this can inspect capabilities or load balance.
        """
        provider_name = requested_provider or self._default_provider
        return self._registry.get_provider(provider_name)
