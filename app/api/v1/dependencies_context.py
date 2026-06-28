"""Context Engine DI Provider."""

from fastapi import Depends

from app.api.v1.dependencies import (
    get_event_bus,
    get_supabase_client,
    get_goal_service,
    get_intent_service,
    get_memory_service,
    get_plan_service,
    get_recommendation_service,
    get_cognitive_trace_service as get_trace_service,
    get_twin_service,
)
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.enterprise_context_repository import EnterpriseContextRepository
from app.services.context_cache import MemoryContextCache
from app.services.context_dependency_graph import build_default_dependency_graph
from app.services.context_engine import ContextEngine
from app.services.context_provider_registry import ContextProviderRegistry
from app.services.context_providers.business_state_provider import (
    BusinessStateContextProvider,
)
from app.services.context_providers.conversation_provider import (
    ConversationContextProvider,
)
from app.services.context_providers.external_provider import (
    ExternalIntegrationContextProvider,
)
from app.services.context_providers.goal_provider import GoalContextProvider
from app.services.context_providers.intent_provider import IntentContextProvider
from app.services.context_providers.memory_provider import MemoryContextProvider
from app.services.context_providers.plan_provider import PlanContextProvider
from app.services.context_providers.recommendation_provider import (
    RecommendationContextProvider,
)
from app.services.context_providers.trace_provider import TraceContextProvider
from app.services.context_providers.twin_provider import TwinContextProvider
from app.services.context_strategies import (
    DefaultContextCompressor,
    DefaultContextRanker,
    DefaultContextWindowBuilder,
)
from app.services.context_validators import DefaultContextValidator
from app.services.conversation_service import ConversationService
from app.models.enterprise_context import ProviderMetadata
from app.models.enums import ContextSource


async def get_context_repository(
    client=Depends(get_supabase_client),
) -> EnterpriseContextRepository:
    return EnterpriseContextRepository(client)


async def get_conversation_repository(
    client=Depends(get_supabase_client),
) -> ConversationRepository:
    return ConversationRepository(client)


async def get_conversation_service(
    repository: ConversationRepository = Depends(get_conversation_repository),
    event_bus=Depends(get_event_bus),
) -> ConversationService:
    return ConversationService(repository=repository, event_bus=event_bus)


async def get_context_registry(
    memory_service=Depends(get_memory_service),
    intent_service=Depends(get_intent_service),
    goal_service=Depends(get_goal_service),
    plan_service=Depends(get_plan_service),
    recommendation_service=Depends(get_recommendation_service),
    twin_service=Depends(get_twin_service),
    conversation_service=Depends(get_conversation_service),
    trace_service=Depends(get_trace_service),
) -> ContextProviderRegistry:
    registry = ContextProviderRegistry()

    registry.register(
        provider=MemoryContextProvider(memory_service),
        metadata=ProviderMetadata(
            source=ContextSource.MEMORY, name="MemoryProvider", version="1.0"
        ),
    )
    registry.register(
        provider=IntentContextProvider(intent_service),
        metadata=ProviderMetadata(
            source=ContextSource.INTENT, name="IntentProvider", version="1.0"
        ),
    )
    registry.register(
        provider=GoalContextProvider(goal_service),
        metadata=ProviderMetadata(
            source=ContextSource.GOAL, name="GoalProvider", version="1.0"
        ),
    )
    registry.register(
        provider=PlanContextProvider(plan_service),
        metadata=ProviderMetadata(
            source=ContextSource.PLAN, name="PlanProvider", version="1.0"
        ),
    )
    registry.register(
        provider=RecommendationContextProvider(recommendation_service),
        metadata=ProviderMetadata(
            source=ContextSource.RECOMMENDATION,
            name="RecommendationProvider",
            version="1.0",
        ),
    )
    registry.register(
        provider=TwinContextProvider(twin_service),
        metadata=ProviderMetadata(
            source=ContextSource.TWIN, name="TwinProvider", version="1.0"
        ),
    )
    registry.register(
        provider=ConversationContextProvider(conversation_service),
        metadata=ProviderMetadata(
            source=ContextSource.CONVERSATION,
            name="ConversationProvider",
            version="1.0",
        ),
    )
    registry.register(
        provider=TraceContextProvider(trace_service),
        metadata=ProviderMetadata(
            source=ContextSource.TRACE, name="TraceProvider", version="1.0"
        ),
    )
    registry.register(
        provider=BusinessStateContextProvider(twin_service),
        metadata=ProviderMetadata(
            source=ContextSource.BUSINESS_STATE,
            name="BusinessStateProvider",
            version="1.0",
        ),
    )
    registry.register(
        provider=ExternalIntegrationContextProvider(),
        metadata=ProviderMetadata(
            source=ContextSource.EXTERNAL, name="ExternalProvider", version="1.0"
        ),
    )

    return registry


# --- Stateless Singletons (Fix Group 9) ---
_dependency_graph = build_default_dependency_graph()
_validator = DefaultContextValidator()
_ranker = DefaultContextRanker()
_compressor = DefaultContextCompressor()
_window_builder = DefaultContextWindowBuilder()


async def get_context_engine(
    registry: ContextProviderRegistry = Depends(get_context_registry),
    repository: EnterpriseContextRepository = Depends(get_context_repository),
    event_bus=Depends(get_event_bus),
    trace_service=Depends(get_trace_service),
) -> ContextEngine:
    return ContextEngine(
        provider_registry=registry,
        dependency_graph=_dependency_graph,
        validator=_validator,
        ranker=_ranker,
        compressor=_compressor,
        window_builder=_window_builder,
        repository=repository,
        event_bus=event_bus,
        trace_service=trace_service,
    )


# Singleton memory cache
_memory_cache = MemoryContextCache()


async def get_context_cache() -> MemoryContextCache:
    return _memory_cache
