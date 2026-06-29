"""AI dependencies for API v1."""

from fastapi import Depends
from app.config import Settings, get_settings
from app.infrastructure.ai.kernel import AIKernel, AbstractAIKernel
from app.infrastructure.ai.providers.gemini_provider import GeminiProvider
from app.infrastructure.ai.registry import ProviderRegistry
from app.infrastructure.ai.router import ProviderRouter
from app.infrastructure.ai.prompts import PromptManager


async def get_ai_kernel(settings: Settings = Depends(get_settings)) -> AbstractAIKernel:
    registry = ProviderRegistry()
    registry.register(GeminiProvider(settings))
    router = ProviderRouter(registry, default_provider="gemini")
    prompt_manager = PromptManager()
    return AIKernel(router, prompt_manager)
