from abc import ABC, abstractmethod
from typing import Dict, Any

import structlog

from app.models.ai import AIRequest, AIResponse, EmbeddingRequest, EmbeddingResponse
from app.services.ai.prompts import PromptManager
from app.services.ai.router import ProviderRouter

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
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the active provider."""
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
            context={"memory_content": text}
        )
        response = await self.generate(request)
        return response.content

    async def health_check(self) -> Dict[str, Any]:
        provider = self._router.get_active_provider()
        status = await provider.health_check()
        return status
