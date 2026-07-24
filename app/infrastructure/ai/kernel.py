from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.infrastructure.ai.prompts.registry import PromptRegistry

import structlog
from pydantic import BaseModel as PydanticBaseModel

from app.infrastructure.ai.budgets.interfaces import IResourceBudget
from app.infrastructure.ai.models import (
    AIRequest,
    AIRequestLifecycle,
    AIResponse,
    AIResponseMetadata,
    ClassifyRequest,
    ClassifyResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    StreamChunk,
    StructuredRequest,
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
    async def generate_structured(
        self, request: AIRequest, response_schema: type[PydanticBaseModel]
    ) -> PydanticBaseModel:
        """Generate a structured Pydantic response."""
        pass

    @abstractmethod
    def stream(self, request: AIRequest) -> AsyncIterator[StreamChunk]:
        """Stream a generated response."""
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
        """Check the health of all registered providers."""
        pass

    @abstractmethod
    async def classify(self, request: ClassifyRequest) -> ClassifyResponse:
        """Perform structured AI classification.
        Retained for backward compatibility. Delegates to generate_structured.
        """
        pass


class AIKernel(AbstractAIKernel):
    """
    Concrete implementation of the AI Kernel.
    Acts purely as an orchestrator, strictly enforcing the R1 rule.
    """

    def __init__(
        self,
        router: ProviderRouter,
        prompt_manager: PromptRegistry | PromptManager | Any,
        budget: IResourceBudget,
    ):
        self._router = router
        self._prompt_manager = prompt_manager
        self._budget = budget

    def _create_lifecycle(self, operation: str) -> AIRequestLifecycle:
        return AIRequestLifecycle(operation=operation)

    async def generate(self, request: AIRequest) -> AIResponse:
        lifecycle = self._create_lifecycle("generate")
        request.lifecycle = lifecycle
        entity_id = "system"  # In a full system, this would come from context/request

        # 1. Resolve prompt
        resolved_prompt = self._prompt_manager.resolve(
            request.prompt_id, request.version, request.context
        )
        lifecycle.prompt_id = request.prompt_id

        # 2. Budget pre-check (estimate cost = 0 for now as true token estimation is complex)
        await self._budget.pre_check(entity_id=entity_id)

        # 3. Route to best provider
        provider = self._router.get_active_provider(getattr(request, "provider", None))
        lifecycle.provider_name = provider.provider_name

        # 4. Bind structured logging
        log = logger.bind(
            lifecycle_id=lifecycle.lifecycle_id,
            operation=lifecycle.operation,
            provider=provider.provider_name,
        )

        # 5. Execute via provider
        async def _do_generate(p, req, prompt):
            return await p.generate(req, prompt)

        response = await self._router.route_with_fallback(
            provider, _do_generate, request, resolved_prompt
        )

        # 6. Record consumption
        await self._budget.record_consumption(
            entity_id=entity_id,
            lifecycle_id=lifecycle.lifecycle_id,
            amount=response.metadata.completion_tokens
            or 0,  # Assuming completion tokens represent consumption
            prompt_tokens=response.metadata.prompt_tokens,
            model=response.metadata.model,
        )

        log.info(
            "AI Kernel generated text",
            model=response.metadata.model,
            latency_ms=response.metadata.latency_ms,
            prompt_tokens=response.metadata.prompt_tokens,
            completion_tokens=response.metadata.completion_tokens,
            prompt_id=request.prompt_id,
        )

        return response

    async def generate_structured(
        self, request: AIRequest, response_schema: type[PydanticBaseModel]
    ) -> PydanticBaseModel:
        lifecycle = self._create_lifecycle("generate_structured")
        request.lifecycle = lifecycle
        entity_id = "system"

        resolved_prompt = self._prompt_manager.resolve(
            request.prompt_id, request.version, request.context
        )
        lifecycle.prompt_id = request.prompt_id

        await self._budget.pre_check(entity_id=entity_id)

        # Route requiring structured_output capability
        provider = self._router.get_provider_for_capability(
            required_capability="supports_structured_output",
            preferred_provider=request.provider if hasattr(request, "provider") else None,
        )
        lifecycle.provider_name = provider.provider_name

        log = logger.bind(
            lifecycle_id=lifecycle.lifecycle_id,
            operation=lifecycle.operation,
            provider=provider.provider_name,
        )

        struct_req = StructuredRequest(
            prompt_text=resolved_prompt,
            output_schema=response_schema,
            system_instruction=request.system_instruction,
            temperature=getattr(request, "temperature", 0.2),
            model=getattr(request, "model", None),
            lifecycle=lifecycle,
        )

        async def _do_generate_structured(p, req):
            return await p.generate_structured(req)

        response = await self._router.route_with_fallback(
            provider, _do_generate_structured, struct_req
        )

        prompt_tokens = 0
        completion_tokens = 0
        model_used = getattr(request, "model", "unknown") or "unknown"

        # Gracefully extract metadata if the underlying provider attached it
        if hasattr(response, "__ai_metadata__"):
            meta = response.__ai_metadata__
            prompt_tokens = getattr(meta, "prompt_tokens", 0) or 0
            completion_tokens = getattr(meta, "completion_tokens", 0) or 0
            model_used = getattr(meta, "model", model_used)

        await self._budget.record_consumption(
            entity_id=entity_id,
            lifecycle_id=lifecycle.lifecycle_id,
            amount=completion_tokens,
            prompt_tokens=prompt_tokens,
            model=model_used,
        )

        log.info(
            "AI Kernel generated structured text",
            prompt_id=request.prompt_id,
        )

        return response

    async def stream(self, request: AIRequest) -> AsyncIterator[StreamChunk]:
        lifecycle = self._create_lifecycle("stream")
        request.lifecycle = lifecycle
        entity_id = "system"

        resolved_prompt = self._prompt_manager.resolve(
            request.prompt_id, request.version, request.context
        )
        lifecycle.prompt_id = request.prompt_id

        await self._budget.pre_check(entity_id=entity_id)

        provider = self._router.get_provider_for_capability(
            required_capability="supports_streaming",
            preferred_provider=getattr(request, "provider", None),
        )
        lifecycle.provider_name = provider.provider_name

        log = logger.bind(
            lifecycle_id=lifecycle.lifecycle_id,
            operation=lifecycle.operation,
            provider=provider.provider_name,
        )

        log.info("AI Kernel started stream", prompt_id=request.prompt_id)

        total_completion_tokens = 0
        prompt_tokens = 0
        model = "unknown"

        async for chunk in provider.stream(request, resolved_prompt):
            if chunk.completion_tokens is not None:
                total_completion_tokens += chunk.completion_tokens
            if chunk.prompt_tokens is not None:
                prompt_tokens = chunk.prompt_tokens
            if hasattr(chunk, "model"):
                model = str(getattr(chunk, "model"))
            yield chunk

        await self._budget.record_consumption(
            entity_id=entity_id,
            lifecycle_id=lifecycle.lifecycle_id,
            amount=total_completion_tokens,
            prompt_tokens=prompt_tokens,
            model=model,
        )

        log.info(
            "AI Kernel finished stream",
            completion_tokens=total_completion_tokens,
            prompt_id=request.prompt_id,
        )

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        lifecycle = self._create_lifecycle("embed")
        entity_id = "system"

        # Embeddings usually don't use the prompt registry
        await self._budget.pre_check(entity_id=entity_id)

        provider = self._router.get_provider_for_capability(
            required_capability="supports_embeddings",
            preferred_provider=getattr(request, "provider", None),
        )
        lifecycle.provider_name = provider.provider_name

        log = logger.bind(
            lifecycle_id=lifecycle.lifecycle_id,
            operation=lifecycle.operation,
            provider=provider.provider_name,
        )

        response = await provider.embed(request)

        await self._budget.record_consumption(
            entity_id=entity_id,
            lifecycle_id=lifecycle.lifecycle_id,
            amount=len(response.vector),  # For embeddings, amount could be vector dimensions
            model=response.metadata.model,
        )

        log.info(
            "AI Kernel generated embedding",
            model=response.metadata.model,
            latency_ms=response.metadata.latency_ms,
            dimensions=len(response.vector),
        )

        return response

    async def summarize(self, text: str) -> str:
        """
        High-level abstraction for the summarization capability.
        Delegates to generate.
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
        Backward compatible fallback delegating to generate_structured.
        """
        from pydantic import create_model

        # Dynamic schema to satisfy generate_structured
        DynamicSchema = create_model("DynamicClassificationSchema")

        gen_req = AIRequest(
            prompt_id=request.prompt_id,
            version=request.version,
            context={"content": request.content, **request.context},
            system_instruction=request.system_instruction,
        )

        response = await self.generate_structured(gen_req, DynamicSchema)

        metadata = AIResponseMetadata(provider="system", model="system", latency_ms=0.0)
        return ClassifyResponse(raw_json=response.model_dump(), metadata=metadata)

    async def health_check(self) -> dict[str, Any]:
        """Check the health of all registered providers."""
        providers = self._router._registry.list_providers()
        results = {}
        for p in providers:
            try:
                results[p.provider_name] = await p.health_check()
            except Exception as e:
                results[p.provider_name] = {"status": "unhealthy", "error": str(e)}
        return {"status": "ok", "providers": results}
