import time
from typing import Any, Dict

from google import genai
from google.genai import types

from app.config import Settings
from app.infrastructure.ai.models import (
    AIRequest,
    AIResponse,
    AIResponseMetadata,
    EmbeddingRequest,
    EmbeddingResponse,
    ProviderError,
)
from app.infrastructure.ai.providers.base import ILLMProvider, ProviderCapabilities
from app.shared.exceptions.errors import ProviderConfigurationError


class GeminiProvider(ILLMProvider):
    """
    Concrete AI Provider for Google Gemini via the google-genai SDK.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        if not settings.gemini_api_key:
            raise ProviderConfigurationError(
                self.provider_name, "GEMINI_API_KEY is not set."
            )
        self.client = genai.Client(api_key=settings.gemini_api_key)

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            provider_name="gemini",
            default_generation_model=self.settings.gemini_flash_model,
            default_embedding_model=self.settings.gemini_embedding_model,
            supports_streaming=True,
            supports_structured_output=True,
            supports_function_calling=True,
            supports_vision=True,
            supports_audio=True,
            max_context_tokens=1_048_576,
            max_output_tokens=8192,
            cost_tier="medium",
            latency_tier="fast",
            reasoning_quality=0.8,
            coding_capability=0.8,
            instruction_following=0.8,
            json_reliability=0.9,
            context_faithfulness=0.8,
            multilingual_quality=0.9,
        )

    async def generate(self, request: AIRequest, prompt_text: str) -> AIResponse:
        model = self.settings.gemini_flash_model

        config_kwargs = {"temperature": 0.7}
        if request.system_instruction:
            config_kwargs["system_instruction"] = request.system_instruction

        config = types.GenerateContentConfig(**config_kwargs)

        start_time = time.time()
        try:
            response = await self.client.aio.models.generate_content(
                model=model,
                contents=prompt_text,
                config=config,
            )
            latency = (time.time() - start_time) * 1000

            # Extract token usage safely based on the SDK structure
            prompt_tokens = (
                getattr(response.usage_metadata, "prompt_token_count", None)
                if hasattr(response, "usage_metadata")
                else None
            )
            completion_tokens = (
                getattr(response.usage_metadata, "candidates_token_count", None)
                if hasattr(response, "usage_metadata")
                else None
            )

            metadata = AIResponseMetadata(
                provider=self.provider_name,
                model=model,
                latency_ms=latency,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
            )

            return AIResponse(content=response.text, metadata=metadata)

        except Exception as e:
            lifecycle_id = request.lifecycle.lifecycle_id if request.lifecycle else None
            raise ProviderError(self.provider_name, "generate", str(e), lifecycle_id=lifecycle_id) from e

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        model = request.model or self.settings.gemini_embedding_model

        start_time = time.time()
        try:
            response = await self.client.aio.models.embed_content(
                model=model,
                contents=request.text,
            )
            latency = (time.time() - start_time) * 1000

            if isinstance(response.embeddings, list):
                vector = response.embeddings[0].values
            else:
                vector = response.embeddings.values

            metadata = AIResponseMetadata(
                provider=self.provider_name,
                model=model,
                latency_ms=latency,
            )

            return EmbeddingResponse(vector=vector, metadata=metadata)

        except Exception as e:
            raise ProviderError(self.provider_name, "embed", str(e)) from e

    async def health_check(self) -> dict[str, Any]:
        """
        Verify Gemini API key configuration and connectivity.
        """
        try:
            # simple generate check
            await self.client.aio.models.generate_content(
                model=self.settings.gemini_flash_model,
                contents="ping",
            )
            return {"status": "healthy", "provider": self.provider_name}
        except Exception as e:
            raise ProviderError(self.provider_name, "health_check", str(e)) from e
