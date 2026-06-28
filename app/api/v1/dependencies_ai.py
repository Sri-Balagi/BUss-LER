"""AI dependencies for API v1."""

from fastapi import Depends
from app.config import Settings, get_settings
from app.services.ai.kernel import AIKernel, AbstractAIKernel
from app.services.ai.providers.gemini_provider import GeminiProvider
from app.services.ai.registry import ProviderRegistry
from app.services.ai.router import ProviderRouter
from app.services.ai.prompts import PromptManager


async def get_ai_kernel(settings: Settings = Depends(get_settings)) -> AbstractAIKernel:
    registry = ProviderRegistry()
    registry.register(GeminiProvider(settings))
    router = ProviderRouter(registry, default_provider="gemini")
    prompt_manager = PromptManager()
    return AIKernel(router, prompt_manager)
