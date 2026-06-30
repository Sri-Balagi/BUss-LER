from typing import Dict

from app.infrastructure.ai.providers.base import AbstractAIProvider
from app.shared.exceptions.errors import ProviderConfigurationError


class ProviderRegistry:
    """
    Holds registered AI Providers.
    """

    def __init__(self):
        self._providers: dict[str, AbstractAIProvider] = {}

    def register(self, provider: AbstractAIProvider) -> None:
        """Register a provider instance."""
        self._providers[provider.provider_name] = provider

    def get_provider(self, name: str) -> AbstractAIProvider:
        """Retrieve a registered provider by name."""
        if name not in self._providers:
            raise ProviderConfigurationError(
                name, f"Provider '{name}' is not registered."
            )
        return self._providers[name]
