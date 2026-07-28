"""LLM Provider Registry for dynamic provider resolution and fallback routing."""

from typing import Dict, List, Optional
from app.domain.intelligence.llm_provider import ILLMProvider
from app.infrastructure.ai.providers.gemini_live_provider import GeminiLiveProvider
from app.application.intelligence.providers import CognitiveSimulatorProvider


class LLMProviderRegistry:
    """Central registry for LLM providers."""

    def __init__(self, default_provider: str = "gemini-flash"):
        self._providers: Dict[str, ILLMProvider] = {}
        self._default_name = default_provider

    def register(self, provider: ILLMProvider) -> None:
        self._providers[provider.provider_name] = provider

    def get_provider(self, name: Optional[str] = None) -> ILLMProvider:
        target = name or self._default_name
        if target in self._providers:
            return self._providers[target]
        if "gemini-flash" in self._providers:
            return self._providers["gemini-flash"]
        if self._providers:
            return next(iter(self._providers.values()))
        
        # Fallback initializer
        fallback = GeminiLiveProvider()
        self.register(fallback)
        return fallback

    def get_providers_chain(self, primary: Optional[str] = None) -> List[ILLMProvider]:
        chain = []
        target = primary or self._default_name
        if target in self._providers:
            chain.append(self._providers[target])
        for name, p in self._providers.items():
            if name != target:
                chain.append(p)
        if not chain:
            fallback = GeminiLiveProvider()
            self.register(fallback)
            chain.append(fallback)
        return chain


ProviderRegistry = LLMProviderRegistry
