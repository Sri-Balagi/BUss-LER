import json
from abc import ABC, abstractmethod
from typing import Any, Dict

import structlog

from app.infrastructure.ai.models import (
    AIRequest,
    AIResponse,
    ClassifyRequest,
    ClassifyResponse,
    EmbeddingRequest,
    EmbeddingResponse,
)
from app.infrastructure.ai.prompts import PromptManager
from app.infrastructure.ai.router import ProviderRouter

logger = structlog.get_logger(__name__)


class AbstractAIKernel(ABC):
    """
    Capability-based AI platform interface for BizOS.
    """

    @abstractmethod
    async def generate(self, request: AIRequest) -> AIResponse:
        """Generate text using a resolved prompt and active provider."""
        pass

    @abstractmethod
    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generate an embedding vector."""
        pass

    @abstractmethod
    async def summarize(self, text: str) -> str:
        """Convenience capability for summarization."""
        pass

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Check the health of the active provider."""
        pass


    @abstractmethod
    async def classify(self, request: ClassifyRequest) -> ClassifyResponse:
        """Perform structured AI classification.

        This is the dedicated cognitive capability for classification tasks.
        It must return a ClassifyResponse whose raw_json has been extracted
        from the provider's response and is ready for Pydantic validation
        by the calling service.

        Contract:
          - The provider must return valid JSON matching the expected schema.
          - ClassifyResponse.raw_json is NOT validated here — the caller
            (e.g., IntentClassifier) validates it against the domain schema.
          - Free-form text responses are rejected.

        Future capabilities (not implemented in M3):
          - reason()
          - reflect()
          - plan()
          - simulate()
        """
        pass


class AIKernel(AbstractAIKernel):
    """
    Concrete implementation of the AI Kernel.
    Manages prompt resolution, provider routing, and execution logging.
    """

    def __init__(self, router: ProviderRouter, prompt_manager: PromptManager):
        self._router = router
        self._prompt_manager = prompt_manager

    async def generate(self, request: AIRequest) -> AIResponse:
        provider = self._router.get_active_provider()

        # 1. Resolve prompt
        resolved_prompt = self._prompt_manager.resolve(
            request.prompt_id, request.version, request.context
        )

        # 2. Execute via provider
        response = await provider.generate(request, resolved_prompt)

        # 3. Log metadata (never content or prompt)
        logger.info(
            "AI Kernel generated text",
            provider=response.metadata.provider,
            model=response.metadata.model,
            latency_ms=response.metadata.latency_ms,
            prompt_tokens=response.metadata.prompt_tokens,
            completion_tokens=response.metadata.completion_tokens,
            prompt_id=request.prompt_id,
        )

        return response

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        provider = self._router.get_active_provider()

        response = await provider.embed(request)

        logger.info(
            "AI Kernel generated embedding",
            provider=response.metadata.provider,
            model=response.metadata.model,
            latency_ms=response.metadata.latency_ms,
            dimensions=len(response.vector),
        )

        return response

    async def summarize(self, text: str) -> str:
        """
        High-level abstraction for the summarization capability.
        """
        request = AIRequest(
            prompt_id="memory_summarization",
            version="v1",
            context={"memory_content": text},
        )
        response = await self.generate(request)
        return response.content

    async def classify(self, request: ClassifyRequest) -> ClassifyResponse:
        """Perform structured AI classification.

        Uses the active provider to generate a structured JSON response.
        Extracts and validates that the response is parseable JSON.
        The calling service is responsible for validating raw_json against
        its expected domain schema (e.g., IntentAnalysis).
        """
        provider = self._router.get_active_provider()

        # Resolve the classification prompt
        resolved_prompt = self._prompt_manager.resolve(
            request.prompt_id,
            request.version,
            {"content": request.content, **request.context},
        )

        # Build a generate request using the classification prompt
        gen_request = AIRequest(
            prompt_id=request.prompt_id,
            version=request.version,
            context={"content": request.content, **request.context},
            system_instruction=request.system_instruction,
        )

        response = await provider.generate(gen_request, resolved_prompt)

        # Extract JSON from the response — reject free-form text
        try:
            # Strip markdown code fences if present
            raw_text = response.content.strip()
            if raw_text.startswith("```"):
                lines = raw_text.split("\n")
                raw_text = "\n".join(lines[1:-1])
            raw_json = json.loads(raw_text)
        except (json.JSONDecodeError, ValueError) as exc:
            raise ValueError(
                f"AI provider returned non-JSON response for classification prompt "
                f"'{request.prompt_id}:{request.version}': {exc}"
            ) from exc

        logger.info(
            "AI Kernel classification completed",
            provider=response.metadata.provider,
            model=response.metadata.model,
            latency_ms=response.metadata.latency_ms,
            prompt_id=request.prompt_id,
            prompt_version=request.version,
        )

        return ClassifyResponse(raw_json=raw_json, metadata=response.metadata)

    async def health_check(self) -> dict[str, Any]:
        provider = self._router.get_active_provider()
        status = await provider.health_check()
        return status
