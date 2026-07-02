"""Tests for the Mock LLM Provider."""

import asyncio
from datetime import UTC, datetime

import pytest
from pydantic import BaseModel

from app.infrastructure.ai.models import (
    AIRequest,
    AIRequestLifecycle,
    EmbeddingRequest,
    ProviderError,
    StructuredOutputError,
    StructuredRequest,
)
from app.infrastructure.ai.providers.mock.provider import MockLLMProvider
from app.infrastructure.ai.providers.mock.scenarios import (
    MockScenarioConfig,
    MockScenarioMode,
)


class DummySchema(BaseModel):
    name: str
    age: int


@pytest.fixture
def mock_provider() -> MockLLMProvider:
    return MockLLMProvider()


@pytest.mark.asyncio
async def test_fixed_response(mock_provider: MockLLMProvider) -> None:
    mock_provider.configure_response("Hello, World!")
    request = AIRequest(prompt_id="test_prompt", context={})

    response = await mock_provider.generate(request, "Hi")

    assert response.content == "Hello, World!"
    assert response.metadata.provider == "mock"
    mock_provider.assert_called_once()
    assert mock_provider.call_log[0].method_name == "generate"


@pytest.mark.asyncio
async def test_structured_response(mock_provider: MockLLMProvider) -> None:
    mock_provider.configure_structured_response({"name": "Alice", "age": 30})
    request = StructuredRequest(prompt_text="test", output_schema=DummySchema)

    result = await mock_provider.generate_structured(request)

    assert isinstance(result, DummySchema)
    assert result.name == "Alice"
    assert result.age == 30
    mock_provider.assert_called_once()


@pytest.mark.asyncio
async def test_structured_response_invalid(mock_provider: MockLLMProvider) -> None:
    # Set invalid data for DummySchema (age should be int)
    mock_provider.configure_structured_response({"name": "Alice", "age": "Not a number"})
    request = StructuredRequest(prompt_text="test", output_schema=DummySchema)

    with pytest.raises(StructuredOutputError):
        await mock_provider.generate_structured(request)


@pytest.mark.asyncio
async def test_streaming_simulation(mock_provider: MockLLMProvider) -> None:
    config = MockScenarioConfig(
        mode=MockScenarioMode.STREAMING_SIMULATION,
        streaming_chunks=["A", "B", "C"],
        mock_prompt_tokens=5,
        mock_completion_tokens=10,
    )
    mock_provider.configure_scenario(config)

    request = AIRequest(prompt_id="test_prompt")
    chunks = []

    async for chunk in mock_provider.stream(request, "prompt"):
        chunks.append(chunk)

    assert len(chunks) == 3
    assert chunks[0].content == "A"
    assert chunks[2].content == "C"
    assert chunks[2].is_final is True
    assert chunks[2].prompt_tokens == 5
    assert chunks[2].completion_tokens == 10
    mock_provider.assert_called_once()


@pytest.mark.asyncio
async def test_provider_unavailable(mock_provider: MockLLMProvider) -> None:
    mock_provider.configure_scenario(MockScenarioConfig(mode=MockScenarioMode.PROVIDER_UNAVAILABLE))
    request = AIRequest(prompt_id="test_prompt")

    with pytest.raises(ProviderError) as exc:
        await mock_provider.generate(request, "test")
    assert exc.value.provider == "mock"
    assert "unavailable" in exc.value.detail


@pytest.mark.asyncio
async def test_failure_simulation_on_nth_call(mock_provider: MockLLMProvider) -> None:
    mock_provider.configure_scenario(
        MockScenarioConfig(
            mode=MockScenarioMode.FAILURE_SIMULATION,
            fail_on_call_number=2,
            error_message="Fail on call 2",
        )
    )
    request = AIRequest(prompt_id="test_prompt")

    # First call succeeds
    response = await mock_provider.generate(request, "test 1")
    assert response.content == "This is a mock response."

    # Second call fails
    with pytest.raises(ProviderError) as exc:
        await mock_provider.generate(request, "test 2")
    assert "Fail on call 2" in exc.value.detail

    mock_provider.assert_called_n_times(2)


@pytest.mark.asyncio
async def test_latency_simulation(mock_provider: MockLLMProvider) -> None:
    mock_provider.configure_scenario(
        MockScenarioConfig(mode=MockScenarioMode.LATENCY_SIMULATION, latency_ms=100)
    )
    request = AIRequest(prompt_id="test_prompt")

    start_time = datetime.now(UTC)
    await mock_provider.generate(request, "test")
    end_time = datetime.now(UTC)

    delta_ms = (end_time - start_time).total_seconds() * 1000
    # Allow some jitter, but it should be around 100ms
    assert delta_ms >= 50


@pytest.mark.asyncio
async def test_lifecycle_propagation(mock_provider: MockLLMProvider) -> None:
    lifecycle = AIRequestLifecycle(operation="generate")
    request = AIRequest(prompt_id="test_prompt", lifecycle=lifecycle)

    await mock_provider.generate(request, "test")
    mock_provider.assert_lifecycle_propagated()

    # Missing lifecycle should trigger assertion error
    request2 = AIRequest(prompt_id="test_prompt")
    await mock_provider.generate(request2, "test2")

    with pytest.raises(AssertionError):
        mock_provider.assert_lifecycle_propagated()


@pytest.mark.asyncio
async def test_embed_and_tokens(mock_provider: MockLLMProvider) -> None:
    request = EmbeddingRequest(text="test embed")
    response = await mock_provider.embed(request)
    assert len(response.vector) > 0

    tokens = await mock_provider.count_tokens("test string")
    assert tokens > 0

    health = await mock_provider.health_check()
    assert health["status"] == "healthy"
