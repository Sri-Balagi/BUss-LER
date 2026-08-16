from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class ILLMProvider(ABC):
    """Base interface for all LLM providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema: type[BaseModel],
        tools: list[Any] | None = None,
        model: str | None = None
    ) -> BaseModel:
        """Generate structured output adhering to a Pydantic schema."""
        pass

    @abstractmethod
    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        tools: list[Any] | None = None,
        model: str | None = None
    ) -> str:
        """Standard chat completion."""
        pass

    @abstractmethod
    async def generate_embeddings(self, text: str, model: str | None = None) -> list[float]:
        """Generate vector embeddings for semantic search."""
        pass
