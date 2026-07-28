"""Embedding Provider Abstraction and Registry for BizOS."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import os
from google import genai

from app.config import get_settings


class IEmbeddingProvider(ABC):
    """Abstract interface for generating vector embeddings."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    @abstractmethod
    def vector_dimension(self) -> int:
        pass

    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Embed a single text string into a vector embedding."""
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of text strings into vector embeddings."""
        pass


class GeminiEmbeddingProvider(IEmbeddingProvider):
    """Embedding provider using Google Gemini's embedding API."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        settings = get_settings()
        self._api_key = api_key or settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
        self._model = model or settings.gemini_embedding_model or "gemini-embedding-001"
        self._client = genai.Client(api_key=self._api_key)

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def vector_dimension(self) -> int:
        return 768

    async def embed_text(self, text: str) -> List[float]:
        response = await self._client.aio.models.embed_content(
            model=self._model,
            contents=text,
        )
        if response and response.embeddings and len(response.embeddings) > 0:
            vals = list(response.embeddings[0].values)
            # Match 768 dimensions if truncated or full
            return vals[:768] if len(vals) >= 768 else vals
        return [0.0] * 768

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        results = []
        for text in texts:
            emb = await self.embed_text(text)
            results.append(emb)
        return results


class LocalFallbackEmbeddingProvider(IEmbeddingProvider):
    """Deterministic local embedding provider fallback for testing."""

    @property
    def provider_name(self) -> str:
        return "local"

    @property
    def vector_dimension(self) -> int:
        return 768

    async def embed_text(self, text: str) -> List[float]:
        # Hash text into deterministic pseudo-embedding vector of 768 dimensions
        import hashlib
        seed = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)
        import random
        rnd = random.Random(seed)
        return [rnd.uniform(-1.0, 1.0) for _ in range(768)]

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [await self.embed_text(t) for t in texts]


class EmbeddingProviderRegistry:
    """Registry manager for resolution of embedding providers."""

    def __init__(self, default_provider: str = "gemini"):
        self._providers: Dict[str, IEmbeddingProvider] = {}
        self._default_provider_name = default_provider

    def register(self, provider: IEmbeddingProvider) -> None:
        self._providers[provider.provider_name] = provider

    def get_provider(self, name: Optional[str] = None) -> IEmbeddingProvider:
        target = name or self._default_provider_name
        if target in self._providers:
            return self._providers[target]
        if self._providers:
            return next(iter(self._providers.values()))
        # Fallback to local
        fallback = LocalFallbackEmbeddingProvider()
        self.register(fallback)
        return fallback
