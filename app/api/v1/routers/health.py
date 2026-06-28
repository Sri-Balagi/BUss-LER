from typing import Dict, Any

from fastapi import APIRouter, Depends

from app.api.v1.dependencies import (
    get_memory_service,
    get_context_repository,
    get_conversation_repository,
    get_context_registry,
)
from app.services.memory_service import MemoryService
from app.repositories.enterprise_context_repository import (
    AbstractEnterpriseContextRepository,
)
from app.repositories.conversation_repository import AbstractConversationRepository
from app.services.context_provider_registry import ContextProviderRegistry
import asyncio


router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/memory", response_model=Dict[str, Any])
async def check_memory_health(
    service: MemoryService = Depends(get_memory_service),
) -> Dict[str, Any]:
    """Check the health of all Memory Engine subsystems."""
    return await service.check_health()


@router.get("/context", response_model=Dict[str, Any])
async def check_context_health(
    repository: AbstractEnterpriseContextRepository = Depends(get_context_repository),
    registry: ContextProviderRegistry = Depends(get_context_registry),
) -> Dict[str, Any]:
    """Check the health of Context Engine subsystems and all providers."""
    repo_health = await repository.health_check()

    # Check all registered providers concurrently
    provider_sources = registry.registered_sources()
    health_tasks = []
    for source in provider_sources:
        provider = registry.get(source)
        health_tasks.append(provider.health_check())

    provider_results = await asyncio.gather(*health_tasks, return_exceptions=True)

    providers_health = {}
    for source, result in zip(provider_sources, provider_results):
        if isinstance(result, Exception):
            providers_health[source.value] = {"status": "error", "detail": str(result)}
        else:
            providers_health[source.value] = result

    repo_health["providers"] = providers_health
    return repo_health


@router.get("/conversations", response_model=Dict[str, Any])
async def check_conversation_health(
    repository: AbstractConversationRepository = Depends(get_conversation_repository),
) -> Dict[str, Any]:
    """Check the health of Conversation Engine subsystems."""
    return await repository.health_check()
