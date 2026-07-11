"""Context Engine DI Provider."""

from fastapi import Depends
from app.bootstrap.container import get_container

from app.infrastructure.cache.context_cache import MemoryContextCache
from app.infrastructure.persistence.postgres.repositories.conversation_repository import ConversationRepository
from app.infrastructure.persistence.postgres.repositories.enterprise_context_repository import EnterpriseContextRepository
from app.application.context.provider_registry import ContextProviderRegistry
from app.application.context.engine import ContextEngine
from app.application.conversation.conversation_service import ConversationService

async def get_context_repository() -> EnterpriseContextRepository:
    return get_container().resolve(EnterpriseContextRepository)

async def get_conversation_repository() -> ConversationRepository:
    return get_container().resolve(ConversationRepository)

async def get_conversation_service() -> ConversationService:
    return get_container().resolve(ConversationService)

async def get_context_registry() -> ContextProviderRegistry:
    return get_container().resolve(ContextProviderRegistry)

async def get_context_engine() -> ContextEngine:
    return get_container().resolve(ContextEngine)

async def get_context_cache() -> MemoryContextCache:
    return get_container().resolve(MemoryContextCache)
