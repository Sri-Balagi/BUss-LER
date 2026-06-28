import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.models.ai import EmbeddingRequest
from app.services.ai.kernel import AIKernel
from app.services.ai.prompts import PromptManager
from app.services.ai.providers.base import AbstractAIProvider
from app.services.ai.registry import ProviderRegistry
from app.services.ai.router import ProviderRouter
from app.services.ai.providers.gemini_provider import GeminiProvider
from app.config import get_settings


# --- Unit Tests ---


@pytest.fixture
def mock_provider():
    provider = AsyncMock(spec=AbstractAIProvider)
    provider.provider_name = "mock_provider"

    mock_generate_response = MagicMock()
    mock_generate_response.content = "Mock summary"
    mock_generate_response.metadata.provider = "mock_provider"
    mock_generate_response.metadata.model = "mock-model"
    mock_generate_response.metadata.latency_ms = 100.0
    mock_generate_response.metadata.prompt_tokens = 10
    mock_generate_response.metadata.completion_tokens = 5
    provider.generate.return_value = mock_generate_response

    mock_embed_response = MagicMock()
    mock_embed_response.vector = [0.1, 0.2, 0.3]
    mock_embed_response.metadata.provider = "mock_provider"
    mock_embed_response.metadata.model = "mock-model"
    mock_embed_response.metadata.latency_ms = 50.0
    provider.embed.return_value = mock_embed_response

    provider.health_check.return_value = {
        "status": "healthy",
        "provider": "mock_provider",
    }
    return provider


@pytest.fixture
def ai_kernel(mock_provider):
    registry = ProviderRegistry()
    registry.register(mock_provider)
    router = ProviderRouter(registry, default_provider="mock_provider")
    prompt_manager = PromptManager()
    return AIKernel(router, prompt_manager)


@pytest.mark.asyncio
async def test_kernel_summarize_capability(ai_kernel, mock_provider):
    result = await ai_kernel.summarize("This is a long memory.")
    assert result == "Mock summary"
    mock_provider.generate.assert_called_once()
    args, _ = mock_provider.generate.call_args
    assert args[0].prompt_id == "memory_summarization"
    assert "This is a long memory." in args[1]


@pytest.mark.asyncio
async def test_kernel_embed_capability(ai_kernel, mock_provider):
    request = EmbeddingRequest(text="Embed this")
    response = await ai_kernel.embed(request)
    assert response.vector == [0.1, 0.2, 0.3]
    assert response.metadata.provider == "mock_provider"
    mock_provider.embed.assert_called_once_with(request)


@pytest.mark.asyncio
async def test_kernel_health_check(ai_kernel, mock_provider):
    status = await ai_kernel.health_check()
    assert status["status"] == "healthy"
    mock_provider.health_check.assert_called_once()


# --- Integration Tests ---


@pytest.fixture
def gemini_kernel():
    settings = get_settings()
    settings.gemini_api_key = "dummy-key"

    with patch("app.services.ai.providers.gemini_provider.genai.Client") as mock_client:
        mock_aio = AsyncMock()
        mock_client.return_value.aio = mock_aio

        # Mock generate
        mock_gen_response = MagicMock()
        mock_gen_response.text = "Mocked gemini summary"
        mock_gen_response.usage_metadata.prompt_token_count = 10
        mock_gen_response.usage_metadata.candidates_token_count = 5
        mock_aio.models.generate_content.return_value = mock_gen_response

        # Mock embed
        mock_embed_response = MagicMock()
        mock_embedding = MagicMock()
        mock_embedding.values = [0.1, 0.2, 0.3]
        mock_embed_response.embeddings = [mock_embedding]
        mock_aio.models.embed_content.return_value = mock_embed_response

        registry = ProviderRegistry()
        registry.register(GeminiProvider(settings))
        router = ProviderRouter(registry, default_provider="gemini")
        prompt_manager = PromptManager()
        yield AIKernel(router, prompt_manager)


@pytest.mark.asyncio
async def test_gemini_integration_summarize(gemini_kernel):
    result = await gemini_kernel.summarize(
        "The user created an AI kernel to route provider requests."
    )
    assert isinstance(result, str)
    assert result == "Mocked gemini summary"


@pytest.mark.asyncio
async def test_gemini_integration_embed(gemini_kernel):
    request = EmbeddingRequest(text="BizOS Memory Engine")
    response = await gemini_kernel.embed(request)
    assert isinstance(response.vector, list)
    assert len(response.vector) > 0
    assert response.metadata.provider == "gemini"


@pytest.mark.asyncio
async def test_gemini_integration_health(gemini_kernel):
    status = await gemini_kernel.health_check()
    assert status["status"] == "healthy"
    assert status["provider"] == "gemini"
