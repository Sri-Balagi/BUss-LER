from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import BaseModel

from app.config import Settings
from app.infrastructure.ai.models import (
    AIRequest,
    StructuredOutputError,
    StructuredRequest,
)
from app.infrastructure.ai.providers.gemini_provider import GeminiProvider


class MockSettings(Settings):
    gemini_api_key: str = "test-key"
    gemini_flash_model: str = "test-model"
    gemini_embedding_model: str = "test-embed-model"


class MySchema(BaseModel):
    name: str
    age: int


@pytest.fixture
def provider():
    settings = MockSettings()
    p = GeminiProvider(settings)
    p.client = MagicMock()
    p.client.aio = MagicMock()
    p.client.aio.models = AsyncMock()
    return p


@pytest.mark.asyncio
async def test_capabilities(provider):
    cap = provider.capabilities
    assert cap.provider_name == "gemini"
    assert cap.supports_structured_output is True
    assert cap.supports_streaming is True


@pytest.mark.asyncio
async def test_generate_structured_success(provider):
    request = StructuredRequest(
        output_schema=MySchema,
        prompt_text="Tell me about John.",
        system_instruction="You are helpful",
    )
    prompt = "Tell me about John."

    # Setup mock response
    mock_response = MagicMock()
    mock_response.parsed = MySchema(name="John", age=30)
    provider.client.aio.models.generate_content.return_value = mock_response

    result = await provider.generate_structured(request, prompt)

    assert isinstance(result, MySchema)
    assert result.name == "John"

    # Verify config
    provider.client.aio.models.generate_content.assert_called_once()
    kwargs = provider.client.aio.models.generate_content.call_args.kwargs
    config = kwargs["config"]
    assert config.response_schema == MySchema
    assert config.response_mime_type == "application/json"


@pytest.mark.asyncio
async def test_generate_structured_failure_not_parsed(provider):
    request = StructuredRequest(output_schema=MySchema, prompt_text="Tell me about John.")

    mock_response = MagicMock()
    del mock_response.parsed  # simulate missing attribute
    provider.client.aio.models.generate_content.return_value = mock_response

    with pytest.raises(StructuredOutputError, match="Failed to parse structured output"):
        await provider.generate_structured(request, "prompt")


@pytest.mark.asyncio
async def test_generate_structured_failure_wrong_type(provider):
    class OtherSchema(BaseModel):
        foo: str

    request = StructuredRequest(output_schema=MySchema, prompt_text="Tell me about John.")

    mock_response = MagicMock()
    mock_response.parsed = OtherSchema(foo="bar")
    provider.client.aio.models.generate_content.return_value = mock_response

    with pytest.raises(StructuredOutputError, match="Parsed response is not an instance of"):
        await provider.generate_structured(request, "prompt")


@pytest.mark.asyncio
async def test_stream(provider):
    request = AIRequest(prompt_id="test-prompt")
    prompt = "Write a story."

    # Mock stream response
    chunk1 = MagicMock()
    chunk1.text = "Once "

    chunk2 = MagicMock()
    chunk2.text = "upon a time."
    chunk2.usage_metadata = MagicMock()
    chunk2.usage_metadata.prompt_token_count = 5
    chunk2.usage_metadata.candidates_token_count = 10

    async def mock_stream():
        yield chunk1
        yield chunk2

    provider.client.aio.models.generate_content_stream.return_value = mock_stream()

    chunks = []
    async for chunk in provider.stream(request, prompt):
        chunks.append(chunk)

    assert len(chunks) == 2

    assert chunks[0].content == "Once "
    assert chunks[0].is_final is False
    assert chunks[0].prompt_tokens is None
    assert chunks[0].completion_tokens is None
    assert chunks[0].error is None

    assert chunks[1].content == "upon a time."
    assert chunks[1].is_final is True
    assert chunks[1].prompt_tokens == 5
    assert chunks[1].completion_tokens == 10
    assert chunks[1].error is None


@pytest.mark.asyncio
async def test_count_tokens(provider):
    mock_response = MagicMock()
    mock_response.total_tokens = 42
    provider.client.aio.models.count_tokens.return_value = mock_response

    count = await provider.count_tokens("Hello world")

    assert count == 42
    provider.client.aio.models.count_tokens.assert_called_once_with(
        model=provider.settings.gemini_flash_model, contents="Hello world"
    )
