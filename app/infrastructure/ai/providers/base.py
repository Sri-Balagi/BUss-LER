"""Provider Abstractions for BizOS.

Defines the abstract contract for AI providers and capabilities.
"""

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, TypeVar

from pydantic import BaseModel

from app.infrastructure.ai.models import (
    AIRequest,
    AIResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    StreamChunk,
    StructuredRequest,
)

T = TypeVar("T", bound=BaseModel)


class ProviderCapabilities(BaseModel):
    """Complete capability declaration for an LLM provider."""
    # Identity
    provider_name: str
    default_generation_model: str
    default_embedding_model: str

    # Technical Capabilities
    supports_streaming: bool = False
    supports_structured_output: bool = False
    supports_function_calling: bool = False
    supports_vision: bool = False
    supports_audio: bool = False
    max_context_tokens: int = 8192
    max_output_tokens: int = 2048

    # Cost Dimensions (USD)
    cost_per_1k_input_tokens: float = 0.0
    cost_per_1k_output_tokens: float = 0.0
    cost_per_embedding: float = 0.0

    # Semantic Capabilities
    reasoning_quality: float = 0.5
    coding_capability: float = 0.5
    instruction_following: float = 0.5
    json_reliability: float = 0.5
    context_faithfulness: float = 0.5
    multilingual_quality: float = 0.5
    
    cost_tier: str = "medium"
    latency_tier: str = "medium"


class ILLMProvider(ABC):
    """Abstract interface for all LLM providers in BizOS."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Canonical identifier."""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> ProviderCapabilities:
        """Self-declared capabilities."""
        pass

    @abstractmethod
    async def generate(self, request: AIRequest, prompt_text: str) -> AIResponse:
        """Generate text from a fully resolved prompt string."""
        pass

    async def generate_structured(self, request: StructuredRequest[T]) -> T:
        """Generate a structured Pydantic object using provider-native schema enforcement."""
        raise NotImplementedError("This provider does not implement generate_structured")

    async def stream(self, request: AIRequest, prompt_text: str) -> AsyncIterator[StreamChunk]:
        """Stream generated text chunk by chunk."""
        raise NotImplementedError("This provider does not implement streaming")
        yield  # Required to make this an async generator function

    @abstractmethod
    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generate a vector embedding for the given text."""
        pass

    async def count_tokens(self, text: str, model: str | None = None) -> int:
        """Count tokens for the given text without generating output."""
        raise NotImplementedError("This provider does not implement count_tokens")

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Verify provider connectivity and configuration."""
        pass

# Backward compatibility alias
AbstractAIProvider = ILLMProvider
