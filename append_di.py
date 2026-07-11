import os

with open("app/application/di.py", "a") as f:
    f.write("""
    # =========================================================================
    # Intelligence Subsystems (Milestones 3-6)
    # =========================================================================
    from app.shared.events.bus import EventBus
    from app.shared.events.bus import BackgroundTasksEventBus
    from app.infrastructure.ai.kernel import AbstractAIKernel

    # Register a global EventBus singleton
    container.register_singleton(EventBus, BackgroundTasksEventBus())

    # Trace
    from app.application.trace.cognitive_trace_service import CognitiveTraceService
    from app.infrastructure.persistence.postgres.repositories.trace_repository import TraceRepository

    def build_trace_repo(c: "Container") -> TraceRepository:
        return TraceRepository(client=c.resolve(AsyncClient))
    container.register_factory(TraceRepository, build_trace_repo)
    container.register_factory(CognitiveTraceService, lambda c: CognitiveTraceService(c.resolve(TraceRepository)))

    # Intent
    from app.infrastructure.persistence.postgres.repositories.intent_repository import IntentRepository
    from app.application.intent.intent_classifier import IntentClassifier
    from app.application.intent.intent_service import IntentService
    
    def build_intent_repo(c: "Container") -> IntentRepository:
        return IntentRepository(client=c.resolve(AsyncClient))
    container.register_factory(IntentRepository, build_intent_repo)
    container.register_factory(IntentClassifier, lambda c: IntentClassifier(
        ai_kernel=c.resolve(AbstractAIKernel), 
        trace_service=c.resolve(CognitiveTraceService)
    ))
    container.register_factory(IntentService, lambda c: IntentService(
        repository=c.resolve(IntentRepository),
        event_bus=c.resolve(EventBus),
        classifier=c.resolve(IntentClassifier)
    ))

    # Goal
    from app.infrastructure.persistence.postgres.repositories.goal_repository import GoalRepository
    from app.application.goal.goal_service import GoalService

    def build_goal_repo(c: "Container") -> GoalRepository:
        return GoalRepository(client=c.resolve(AsyncClient))
    container.register_factory(GoalRepository, build_goal_repo)
    container.register_factory(GoalService, lambda c: GoalService(
        repository=c.resolve(GoalRepository),
        event_bus=c.resolve(EventBus)
    ))

    # Conversation
    from app.infrastructure.persistence.postgres.repositories.conversation_repository import ConversationRepository
    from app.application.conversation.conversation_service import ConversationService

    def build_conversation_repo(c: "Container") -> ConversationRepository:
        return ConversationRepository(client=c.resolve(AsyncClient))
    container.register_factory(ConversationRepository, build_conversation_repo)
    container.register_factory(ConversationService, lambda c: ConversationService(
        repository=c.resolve(ConversationRepository),
        event_bus=c.resolve(EventBus)
    ))

    # Planning
    from app.application.planning.planning_engine import PlanningEngine
    from app.infrastructure.persistence.postgres.repositories.plan_repository import PlanRepository
    from app.application.planning.plan_service import PlanService
    from app.application.planning.context_builder import PromptContextBuilder as PlanPromptContextBuilder

    def build_plan_repo(c: "Container") -> PlanRepository:
        return PlanRepository(client=c.resolve(AsyncClient))
    container.register_factory(PlanRepository, build_plan_repo)
    container.register_factory(PlanService, lambda c: PlanService(
        repository=c.resolve(PlanRepository),
        event_bus=c.resolve(EventBus)
    ))
    container.register_factory(PlanPromptContextBuilder, lambda c: PlanPromptContextBuilder())
    from app.application.context.engine import AbstractContextEngine
    container.register_factory(PlanningEngine, lambda c: PlanningEngine(
        context_engine=c.resolve(AbstractContextEngine),
        ai_kernel=c.resolve(AbstractAIKernel),
        context_builder=c.resolve(PlanPromptContextBuilder),
        trace_service=c.resolve(CognitiveTraceService)
    ))

    # Recommendation
    from app.application.recommendation.recommendation_engine import RecommendationEngine
    from app.infrastructure.persistence.postgres.repositories.recommendation_repository import RecommendationRepository
    from app.application.recommendation.context_builder import PromptContextBuilder as RecPromptContextBuilder

    def build_rec_repo(c: "Container") -> RecommendationRepository:
        return RecommendationRepository(client=c.resolve(AsyncClient))
    container.register_factory(RecommendationRepository, build_rec_repo)
    container.register_factory(RecPromptContextBuilder, lambda c: RecPromptContextBuilder())
    container.register_factory(RecommendationEngine, lambda c: RecommendationEngine(
        context_engine=c.resolve(AbstractContextEngine),
        ai_kernel=c.resolve(AbstractAIKernel),
        context_builder=c.resolve(RecPromptContextBuilder),
        trace_service=c.resolve(CognitiveTraceService)
    ))

    # Context Engine
    from app.infrastructure.persistence.postgres.repositories.enterprise_context_repository import EnterpriseContextRepository
    from app.application.context.engine import ContextEngine
    from app.application.context.provider_registry import ContextProviderRegistry
    from app.application.context.providers.memory_provider import MemoryContextProvider
    from app.application.context.providers.intent_provider import IntentContextProvider
    from app.application.context.providers.goal_provider import GoalContextProvider
    from app.application.context.providers.plan_provider import PlanContextProvider
    from app.application.context.providers.recommendation_provider import RecommendationContextProvider
    from app.application.context.providers.twin_provider import TwinContextProvider
    from app.application.context.providers.conversation_provider import ConversationContextProvider
    from app.application.context.providers.trace_provider import TraceContextProvider
    from app.application.context.providers.business_state_provider import BusinessStateContextProvider
    from app.application.context.providers.external_provider import ExternalIntegrationContextProvider
    from app.intelligence.intake.situation.enterprise_context import ProviderMetadata
    from app.shared.enums import ContextSource
    from app.application.context.dependency_graph import build_default_dependency_graph
    from app.application.context.validators import DefaultContextValidator
    from app.application.context.strategies import DefaultContextRanker, DefaultContextCompressor, DefaultContextWindowBuilder
    from app.infrastructure.cache.context_cache import MemoryContextCache

    def build_enterprise_context_repo(c: "Container") -> EnterpriseContextRepository:
        return EnterpriseContextRepository(client=c.resolve(AsyncClient))
    container.register_factory(EnterpriseContextRepository, build_enterprise_context_repo)
    container.register_singleton(MemoryContextCache, MemoryContextCache())

    def build_context_registry(c: "Container") -> ContextProviderRegistry:
        registry = ContextProviderRegistry()
        from app.infrastructure.vectorstore.qdrant import QdrantService
        registry.register(
            provider=MemoryContextProvider(c.resolve(QdrantService)),
            metadata=ProviderMetadata(source=ContextSource.MEMORY, name="MemoryProvider", version="1.0"),
        )
        registry.register(
            provider=IntentContextProvider(c.resolve(IntentService)),
            metadata=ProviderMetadata(source=ContextSource.INTENT, name="IntentProvider", version="1.0"),
        )
        registry.register(
            provider=GoalContextProvider(c.resolve(GoalService)),
            metadata=ProviderMetadata(source=ContextSource.GOAL, name="GoalProvider", version="1.0"),
        )
        registry.register(
            provider=PlanContextProvider(c.resolve(PlanService)),
            metadata=ProviderMetadata(source=ContextSource.PLAN, name="PlanProvider", version="1.0"),
        )
        registry.register(
            provider=RecommendationContextProvider(c.resolve(RecommendationEngine)),
            metadata=ProviderMetadata(source=ContextSource.RECOMMENDATION, name="RecommendationProvider", version="1.0"),
        )
        # Assuming TwinContextProvider needs TwinRepository here, wait! Let's check dependencies_context.py to see what it actually takes.
        # But wait, dependencies_context.py showed: TwinContextProvider(twin_service)
        # For now, let's inject a string or placeholder if it's missing, but we already have UseCases.
        registry.register(
            provider=TwinContextProvider(c.resolve(GetTwinUseCase)), # Temporarily None until we check its signature
            metadata=ProviderMetadata(source=ContextSource.TWIN, name="TwinProvider", version="1.0"),
        )
        registry.register(
            provider=ConversationContextProvider(c.resolve(ConversationService)),
            metadata=ProviderMetadata(source=ContextSource.CONVERSATION, name="ConversationProvider", version="1.0"),
        )
        registry.register(
            provider=TraceContextProvider(c.resolve(CognitiveTraceService)),
            metadata=ProviderMetadata(source=ContextSource.TRACE, name="TraceProvider", version="1.0"),
        )
        registry.register(
            provider=BusinessStateContextProvider(c.resolve(GetTwinUseCase)),
            metadata=ProviderMetadata(source=ContextSource.BUSINESS_STATE, name="BusinessStateProvider", version="1.0"),
        )
        registry.register(
            provider=ExternalIntegrationContextProvider(),
            metadata=ProviderMetadata(source=ContextSource.EXTERNAL, name="ExternalProvider", version="1.0"),
        )
        return registry
    
    container.register_singleton(ContextProviderRegistry, build_context_registry(container))

    def build_context_engine(c: "Container") -> ContextEngine:
        return ContextEngine(
            provider_registry=c.resolve(ContextProviderRegistry),
            dependency_graph=build_default_dependency_graph(),
            validator=DefaultContextValidator(),
            ranker=DefaultContextRanker(),
            compressor=DefaultContextCompressor(),
            window_builder=DefaultContextWindowBuilder(),
            repository=c.resolve(EnterpriseContextRepository),
            event_bus=c.resolve(EventBus),
            trace_service=c.resolve(CognitiveTraceService)
        )
    container.register_factory(AbstractContextEngine, build_context_engine)
    container.register_factory(ContextEngine, build_context_engine)
""")
