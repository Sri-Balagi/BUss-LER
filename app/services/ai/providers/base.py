from abc import ABC, abstractmethod
from typing import Dict, Any

from app.models.ai import AIRequest, AIResponse, EmbeddingRequest, EmbeddingResponse


class AbstractAIProvider(ABC):
    """
    Abstract interface for AI Providers.
    Any concrete provider (Gemini, OpenAI, Local, etc.) must implement this interface.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the canonical name of the provider."""
        pass

    @abstractmethod
    async def generate(self, request: AIRequest, prompt_text: str) -> AIResponse:
        """
        Generate text based on a fully resolved prompt.
        """
        pass

    @abstractmethod
    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """
        Generate vector embedding for the given text.
        """
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Verify provider configuration and connectivity.
        Returns a dictionary with status details.
        """
        pass
