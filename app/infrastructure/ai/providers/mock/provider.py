"""Mock LLM Provider Implementation."""

import asyncio
from collections.abc import AsyncIterator
from typing import Any, TypeVar

from pydantic import BaseModel

from app.infrastructure.ai.models import (
    AIRequest,
    AIResponse,
    AIResponseMetadata,
    EmbeddingRequest,
    EmbeddingResponse,
    ProviderError,
    StreamChunk,
    StructuredOutputError,
    StructuredRequest,
)
from app.infrastructure.ai.providers.base import ILLMProvider, ProviderCapabilities
from app.infrastructure.ai.providers.mock.scenarios import (
    MockScenarioConfig,
    MockScenarioMode,
    ProviderCall,
)

T = TypeVar("T", bound=BaseModel)


class MockLLMProvider(ILLMProvider):
    """Deterministic mock provider for unit and integration testing."""

    def __init__(self, provider_name: str = "mock") -> None:
        self.reset()
        self._provider_name = provider_name
        self._capabilities = ProviderCapabilities(
            provider_name=provider_name,
            default_generation_model="mock-gen-model",
            default_embedding_model="mock-embed-model",
            supports_streaming=True,
            supports_structured_output=True,
            supports_function_calling=True,
            cost_tier="budget",
            latency_tier="fast",
        )

    def reset(self) -> None:
        """Reset the call log and scenario configuration."""
        self.call_log: list[ProviderCall] = []
        self._scenario = MockScenarioConfig()

    @property
    def call_count(self) -> int:
        return len(self.call_log)

    @property
    def provider_name(self) -> str:
        return self._provider_name

    @property
    def capabilities(self) -> ProviderCapabilities:
        return self._capabilities

    def configure_scenario(self, config: MockScenarioConfig) -> None:
        """Configure the provider for a specific edge-case scenario."""
        self._scenario = config

    def configure_response(self, text: str) -> None:
        """Helper to quickly set a fixed text response."""
        self._scenario.mode = MockScenarioMode.FIXED_RESPONSE
        self._scenario.default_text_response = text

    def configure_structured_response(self, data: dict[str, Any]) -> None:
        """Helper to quickly set a fixed structured response."""
        self._scenario.mode = MockScenarioMode.STRUCTURED_RESPONSE
        self._scenario.default_structured_response = data

    def _record_call(self, method_name: str, **kwargs: Any) -> None:
        """Record an invocation into the call log."""
        lifecycle_id = None
        req = kwargs.get("request") or kwargs.get("structured_request")
        if req and getattr(req, "lifecycle", None):
            lifecycle_id = req.lifecycle.lifecycle_id

        self.call_log.append(
            ProviderCall(
                method_name=method_name,
                lifecycle_id=lifecycle_id,
                **{k: v for k, v in kwargs.items() if k in ProviderCall.model_fields},
            )
        )

    async def _simulate_scenario_conditions(self) -> None:
        """Applies delays or throws errors based on the active scenario."""
        if self._scenario.mode == MockScenarioMode.PROVIDER_UNAVAILABLE:
            raise ProviderError("mock", "api_call", "Provider is unavailable (simulated)")

        if self._scenario.mode == MockScenarioMode.FAILURE_SIMULATION:
            if self.call_count == self._scenario.fail_on_call_number:
                raise ProviderError("mock", "api_call", self._scenario.error_message)

        if self._scenario.mode == MockScenarioMode.TIMEOUT_SIMULATION:
            raise ProviderError("mock", "api_call", "Provider timeout (simulated)")

        if self._scenario.mode == MockScenarioMode.LATENCY_SIMULATION:
            if self._scenario.latency_ms > 0:
                await asyncio.sleep(self._scenario.latency_ms / 1000.0)

    async def generate(self, request: AIRequest, prompt_text: str) -> AIResponse:
        self._record_call("generate", request=request, prompt_text=prompt_text)
        await self._simulate_scenario_conditions()

        metadata = AIResponseMetadata(
            provider=self.provider_name,
            model="mock-gen-model",
            latency_ms=self._scenario.latency_ms,
            prompt_tokens=self._scenario.mock_prompt_tokens,
            completion_tokens=self._scenario.mock_completion_tokens,
        )

        return AIResponse(
            content=self._scenario.default_text_response,
            metadata=metadata,
        )

    async def generate_structured(self, request: StructuredRequest[T]) -> T:
        self._record_call("generate_structured", structured_request=request)
        await self._simulate_scenario_conditions()

        data = self._scenario.default_structured_response or {}
        try:
            return request.output_schema.model_validate(data)
        except Exception as e:
            raise StructuredOutputError(
                self.provider_name,
                "generate_structured",
                "Schema validation failed in mock provider",
            ) from e

    async def stream(self, request: AIRequest, prompt_text: str) -> AsyncIterator[StreamChunk]:
        self._record_call("stream", request=request, prompt_text=prompt_text)
        await self._simulate_scenario_conditions()

        if self._scenario.mode != MockScenarioMode.STREAMING_SIMULATION:
            chunks = [self._scenario.default_text_response]
        else:
            chunks = self._scenario.streaming_chunks

        for i, chunk_text in enumerate(chunks):
            is_final = i == len(chunks) - 1

            if (
                self._scenario.mode == MockScenarioMode.LATENCY_SIMULATION
                and self._scenario.latency_ms > 0
            ):
                await asyncio.sleep(self._scenario.latency_ms / 1000.0)

            yield StreamChunk(
                content=chunk_text,
                is_final=is_final,
                prompt_tokens=self._scenario.mock_prompt_tokens if is_final else None,
                completion_tokens=self._scenario.mock_completion_tokens if is_final else None,
            )

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        self._record_call("embed", embedding_request=request)
        await self._simulate_scenario_conditions()

        metadata = AIResponseMetadata(
            provider=self.provider_name,
            model=request.model or "mock-embed-model",
            latency_ms=self._scenario.latency_ms,
        )
        return EmbeddingResponse(
            vector=[0.1, 0.2, 0.3],
            metadata=metadata,
        )

    async def count_tokens(self, text: str, model: str | None = None) -> int:
        self._record_call("count_tokens", prompt_text=text)
        await self._simulate_scenario_conditions()

        if self._scenario.mode == MockScenarioMode.TOKEN_LIMIT_SIMULATION:
            return self._scenario.mock_prompt_tokens

        return len(text) // 4

    async def health_check(self) -> dict[str, Any]:
        self._record_call("health_check")
        await self._simulate_scenario_conditions()
        return {"status": "healthy", "provider": self.provider_name}

    def assert_called_once(self) -> None:
        """Assert the provider was called exactly once."""
        assert self.call_count == 1, f"Expected 1 call, got {self.call_count}"

    def assert_called_n_times(self, n: int) -> None:
        """Assert the provider was called exactly N times."""
        assert self.call_count == n, f"Expected {n} calls, got {self.call_count}"

    def assert_lifecycle_propagated(self) -> None:
        """Assert that every call had a lifecycle ID (except health checks)."""
        for call in self.call_log:
            if call.method_name not in ["health_check", "count_tokens"]:
                assert call.lifecycle_id is not None, (
                    f"Call {call.method_name} missing lifecycle ID"
                )
