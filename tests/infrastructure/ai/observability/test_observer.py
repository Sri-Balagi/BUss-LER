"""Tests for ProviderObserver."""

import pytest
from pydantic import BaseModel
from structlog.testing import capture_logs

from app.infrastructure.ai.models import (
    AIRequest,
    EmbeddingRequest,
    ProviderError,
    StructuredOutputError,
    StructuredRequest,
)
from app.infrastructure.ai.observability.metrics import ProviderObserver
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


@pytest.fixture
def observer(mock_provider: MockLLMProvider) -> ProviderObserver:
    return ProviderObserver(mock_provider)


@pytest.mark.asyncio
async def test_observer_delegates_properties(observer: ProviderObserver, mock_provider: MockLLMProvider) -> None:
    """Verify observer passes through properties accurately."""
    assert observer.provider_name == mock_provider.provider_name
    assert observer.capabilities == mock_provider.capabilities


@pytest.mark.asyncio
async def test_generate_success_observability(observer: ProviderObserver, mock_provider: MockLLMProvider) -> None:
    """Verify generate logs and records metrics properly."""
    mock_provider.configure_response("Test response")
    request = AIRequest(prompt_id="test_prompt", context={})

    with capture_logs() as cap_logs:
        response = await observer.generate(request, "Hello")

    assert response.content == "Test response"

    # Check that structlog was called
    log_events = [event["event"] for event in cap_logs]
    assert "llm_generate_started" in log_events
    assert "llm_generate_completed" in log_events

    # Check that bound variables exist on the complete event
    complete_log = next(event for event in cap_logs if event["event"] == "llm_generate_completed")
    assert "duration_s" in complete_log
    assert "lifecycle_id" in complete_log
    assert complete_log["provider"] == "mock"
    assert complete_log["operation"] == "generate"
    # Ensure no prompt content is logged
    for k, v in complete_log.items():
        assert "Hello" not in str(v)


@pytest.mark.asyncio
async def test_generate_error_observability(observer: ProviderObserver, mock_provider: MockLLMProvider) -> None:
    """Verify errors are logged and propagated during generate."""
    mock_provider.configure_scenario(
        MockScenarioConfig(mode=MockScenarioMode.PROVIDER_UNAVAILABLE)
    )
    request = AIRequest(prompt_id="test_prompt")

    with capture_logs() as cap_logs:
        with pytest.raises(ProviderError):
            await observer.generate(request, "Hello")

    log_events = [event["event"] for event in cap_logs]
    assert "llm_generate_started" in log_events
    assert "llm_generate_failed" in log_events

    failed_log = next(event for event in cap_logs if event["event"] == "llm_generate_failed")
    assert failed_log["error_type"] == "ProviderError"
    assert "duration_s" in failed_log


@pytest.mark.asyncio
async def test_generate_structured_success(observer: ProviderObserver, mock_provider: MockLLMProvider) -> None:
    mock_provider.configure_structured_response({"name": "Alice", "age": 30})
    request = StructuredRequest(prompt_text="test", output_schema=DummySchema)

    with capture_logs() as cap_logs:
        result = await observer.generate_structured(request)

    assert isinstance(result, DummySchema)
    assert result.name == "Alice"

    log_events = [event["event"] for event in cap_logs]
    assert "llm_generate_structured_started" in log_events
    assert "llm_generate_structured_completed" in log_events


@pytest.mark.asyncio
async def test_generate_structured_error(observer: ProviderObserver, mock_provider: MockLLMProvider) -> None:
    mock_provider.configure_structured_response({"name": "Alice", "age": "Not a number"})
    request = StructuredRequest(prompt_text="test", output_schema=DummySchema)

    with capture_logs() as cap_logs:
        with pytest.raises(StructuredOutputError):
            await observer.generate_structured(request)

    log_events = [event["event"] for event in cap_logs]
    assert "llm_generate_structured_failed" in log_events
    failed_log = next(event for event in cap_logs if event["event"] == "llm_generate_structured_failed")
    assert failed_log["error_type"] == "StructuredOutputError"


@pytest.mark.asyncio
async def test_stream_success(observer: ProviderObserver, mock_provider: MockLLMProvider) -> None:
    config = MockScenarioConfig(
        mode=MockScenarioMode.STREAMING_SIMULATION,
        streaming_chunks=["A", "B"],
        mock_prompt_tokens=5,
        mock_completion_tokens=10,
    )
    mock_provider.configure_scenario(config)

    request = AIRequest(prompt_id="test_prompt")

    with capture_logs() as cap_logs:
        chunks = []
        async for chunk in observer.stream(request, "prompt"):
            chunks.append(chunk)

    assert len(chunks) == 2

    log_events = [event["event"] for event in cap_logs]
    assert "llm_stream_started" in log_events
    assert "llm_stream_completed" in log_events

    complete_log = next(event for event in cap_logs if event["event"] == "llm_stream_completed")
    assert complete_log["prompt_tokens"] == 5
    assert complete_log["completion_tokens"] == 10


@pytest.mark.asyncio
async def test_embed_success(observer: ProviderObserver, mock_provider: MockLLMProvider) -> None:
    request = EmbeddingRequest(text="test text")

    with capture_logs() as cap_logs:
        response = await observer.embed(request)

    assert len(response.vector) > 0

    log_events = [event["event"] for event in cap_logs]
    assert "llm_embed_started" in log_events
    assert "llm_embed_completed" in log_events


@pytest.mark.asyncio
async def test_count_tokens(observer: ProviderObserver, mock_provider: MockLLMProvider) -> None:
    with capture_logs() as cap_logs:
        count = await observer.count_tokens("test text")

    assert count > 0

    log_events = [event["event"] for event in cap_logs]
    assert "llm_count_tokens_started" in log_events
    assert "llm_count_tokens_completed" in log_events


@pytest.mark.asyncio
async def test_health_check(observer: ProviderObserver, mock_provider: MockLLMProvider) -> None:
    health = await observer.health_check()
    assert health["status"] == "healthy"


@pytest.mark.asyncio
async def test_unexpected_error_observability(observer: ProviderObserver, mock_provider: MockLLMProvider) -> None:
    """Verify unexpected errors are caught, logged, and re-raised."""
    
    # We'll patch the generate method to raise a raw ValueError
    original_generate = mock_provider.generate
    
    async def fake_generate(*args, **kwargs):
        raise ValueError("Unexpected boom")
        
    mock_provider.generate = fake_generate  # type: ignore
    
    request = AIRequest(prompt_id="test_prompt")
    with capture_logs() as cap_logs:
        with pytest.raises(ValueError, match="Unexpected boom"):
            await observer.generate(request, "Hello")
            
    log_events = [event["event"] for event in cap_logs]
    assert "llm_generate_failed_unexpected" in log_events
    
    # Restore
    mock_provider.generate = original_generate  # type: ignore
    
    # Same for generate_structured
    original_generate_structured = mock_provider.generate_structured
    async def fake_generate_structured(*args, **kwargs):
        raise ValueError("Unexpected boom")
    mock_provider.generate_structured = fake_generate_structured  # type: ignore
    
    structured_request = StructuredRequest(prompt_text="test", output_schema=DummySchema)
    with capture_logs() as cap_logs:
        with pytest.raises(ValueError):
            await observer.generate_structured(structured_request)
    assert "llm_generate_structured_failed_unexpected" in [e["event"] for e in cap_logs]
    mock_provider.generate_structured = original_generate_structured  # type: ignore
    
    # Same for stream
    original_stream = mock_provider.stream
    async def fake_stream(*args, **kwargs):
        raise ValueError("Unexpected boom")
        yield  # make it a generator
    mock_provider.stream = fake_stream  # type: ignore
    
    with capture_logs() as cap_logs:
        with pytest.raises(ValueError):
            async for _ in observer.stream(request, "Hello"):
                pass
    assert "llm_stream_failed_unexpected" in [e["event"] for e in cap_logs]
    mock_provider.stream = original_stream  # type: ignore
    
    # Same for embed
    original_embed = mock_provider.embed
    async def fake_embed(*args, **kwargs):
        raise ValueError("Unexpected boom")
    mock_provider.embed = fake_embed  # type: ignore
    
    embed_request = EmbeddingRequest(text="test")
    with capture_logs() as cap_logs:
        with pytest.raises(ValueError):
            await observer.embed(embed_request)
    assert "llm_embed_failed_unexpected" in [e["event"] for e in cap_logs]
    mock_provider.embed = original_embed  # type: ignore
    
    # Same for count_tokens
    original_count_tokens = mock_provider.count_tokens
    async def fake_count_tokens(*args, **kwargs):
        raise ValueError("Unexpected boom")
    mock_provider.count_tokens = fake_count_tokens  # type: ignore
    
    with capture_logs() as cap_logs:
        with pytest.raises(ValueError):
            await observer.count_tokens("test")
    assert "llm_count_tokens_failed_unexpected" in [e["event"] for e in cap_logs]
    mock_provider.count_tokens = original_count_tokens  # type: ignore
