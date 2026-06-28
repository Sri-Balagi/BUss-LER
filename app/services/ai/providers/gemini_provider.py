import time
from typing import Dict, Any

from google import genai
from google.genai import types

from app.config import Settings
from app.models.ai import (
    AIRequest,
    AIResponse,
    AIResponseMetadata,
    EmbeddingRequest,
    EmbeddingResponse,
)
from app.models.exceptions import AIKernelError, ProviderConfigurationError
from app.services.ai.providers.base import AbstractAIProvider


class GeminiProvider(AbstractAIProvider):
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
            raise AIKernelError(self.provider_name, "generate", str(e)) from e

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
            raise AIKernelError(self.provider_name, "embed", str(e)) from e

    async def health_check(self) -> Dict[str, Any]:
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
            raise AIKernelError(self.provider_name, "health_check", str(e)) from e
