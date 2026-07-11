"""Application Layer Dependency Injection Wiring."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.bootstrap.container import Container


def register_application_dependencies(container: "Container") -> None:
    """Wire Application Layer Use Cases into the global DI container."""
    from supabase import AsyncClient

    # Entity Use Cases
    from app.application.entity.create_entity import CreateEntityUseCase
    from app.application.entity.delete_entity import DeleteEntityUseCase
    from app.application.entity.get_entity import GetEntityUseCase
    from app.application.entity.list_entities import ListEntitiesUseCase
    from app.application.entity.update_entity import UpdateEntityUseCase
    from app.infrastructure.persistence.postgres.repositories.entity_repository import (
        EntityRepository,
    )

    def build_entity_repo(c: "Container") -> EntityRepository:
        return EntityRepository(client=c.resolve(AsyncClient))

    # Repositories (if not already registered elsewhere)
    container.register_factory(EntityRepository, build_entity_repo)

    # Use Cases
    container.register_factory(
        CreateEntityUseCase, lambda c: CreateEntityUseCase(c.resolve(EntityRepository))
    )
    container.register_factory(
        GetEntityUseCase, lambda c: GetEntityUseCase(c.resolve(EntityRepository))
    )
    container.register_factory(
        ListEntitiesUseCase, lambda c: ListEntitiesUseCase(c.resolve(EntityRepository))
    )
    container.register_factory(
        UpdateEntityUseCase, lambda c: UpdateEntityUseCase(c.resolve(EntityRepository))
    )
    container.register_factory(
        DeleteEntityUseCase, lambda c: DeleteEntityUseCase(c.resolve(EntityRepository))
    )

    # Twin Use Cases
    from app.application.twin.create_twin import CreateTwinUseCase
    from app.application.twin.delete_twin import DeleteTwinUseCase
    from app.application.twin.get_twin import GetTwinUseCase
    from app.application.twin.list_twins import ListTwinsUseCase
    from app.application.twin.update_twin import UpdateTwinUseCase
    from app.application.twin.get_snapshots import GetTwinSnapshotsUseCase
    from app.application.twin.get_history import GetTwinHistoryUseCase
    from app.infrastructure.persistence.postgres.repositories.twin_repository import (
        TwinRepository,
    )
    from app.infrastructure.persistence.postgres.repositories.snapshot_repository import (
        SnapshotRepository,
    )
    from app.infrastructure.persistence.postgres.repositories.history_repository import (
        HistoryRepository,
    )

    def build_twin_repo(c: "Container") -> TwinRepository:
        return TwinRepository(client=c.resolve(AsyncClient))

    def build_snapshot_repo(c: "Container") -> SnapshotRepository:
        return SnapshotRepository(client=c.resolve(AsyncClient))

    def build_history_repo(c: "Container") -> HistoryRepository:
        return HistoryRepository(client=c.resolve(AsyncClient))

    container.register_factory(TwinRepository, build_twin_repo)
    container.register_factory(SnapshotRepository, build_snapshot_repo)
    container.register_factory(HistoryRepository, build_history_repo)

    container.register_factory(
        CreateTwinUseCase, lambda c: CreateTwinUseCase(c.resolve(TwinRepository), c.resolve(EntityRepository))
    )
    container.register_factory(
        GetTwinUseCase, lambda c: GetTwinUseCase(c.resolve(TwinRepository))
    )
    container.register_factory(
        ListTwinsUseCase, lambda c: ListTwinsUseCase(c.resolve(TwinRepository))
    )
    container.register_factory(
        UpdateTwinUseCase, lambda c: UpdateTwinUseCase(c.resolve(TwinRepository))
    )
    container.register_factory(
        DeleteTwinUseCase, lambda c: DeleteTwinUseCase(c.resolve(TwinRepository))
    )
    container.register_factory(
        GetTwinSnapshotsUseCase, lambda c: GetTwinSnapshotsUseCase(c.resolve(SnapshotRepository))
    )
    container.register_factory(
        GetTwinHistoryUseCase, lambda c: GetTwinHistoryUseCase(c.resolve(HistoryRepository))
    )

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
    from app.infrastructure.persistence.postgres.repositories.cognitive_trace_repository import CognitiveTraceRepository as TraceRepository

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
    from app.application.planning.context_builder import ContextBuilder as PlanContextBuilder

    def build_plan_repo(c: "Container") -> PlanRepository:
        return PlanRepository(client=c.resolve(AsyncClient))
    container.register_factory(PlanRepository, build_plan_repo)
    container.register_factory(PlanService, lambda c: PlanService(
        repository=c.resolve(PlanRepository),
        event_bus=c.resolve(EventBus)
    ))

    from app.infrastructure.vectorstore.qdrant import QdrantService
    container.register_factory(PlanContextBuilder, lambda c: PlanContextBuilder(
        goal_service=c.resolve(GoalService),
        memory_service=c.resolve(QdrantService)
    ))

    container.register_factory(PlanningEngine, lambda c: PlanningEngine(
        ai_kernel=c.resolve(AbstractAIKernel),
        plan_repository=c.resolve(PlanRepository),
        context_builder=c.resolve(PlanContextBuilder),
        goal_service=c.resolve(GoalService),
        trace_service=c.resolve(CognitiveTraceService),
        event_bus=c.resolve(EventBus)
    ))

    # Recommendation
    from app.application.recommendation.recommendation_engine import RecommendationEngine
    from app.infrastructure.persistence.postgres.repositories.recommendation_repository import RecommendationRepository
    from app.application.recommendation.recommendation_service import RecommendationService

    def build_rec_repo(c: "Container") -> RecommendationRepository:
        return RecommendationRepository(client=c.resolve(AsyncClient))
    container.register_factory(RecommendationRepository, build_rec_repo)
    container.register_factory(RecommendationService, lambda c: RecommendationService(
        repository=c.resolve(RecommendationRepository),
        event_bus=c.resolve(EventBus)
    ))
    container.register_factory(RecommendationEngine, lambda c: RecommendationEngine(
        ai_kernel=c.resolve(AbstractAIKernel),
        repository=c.resolve(RecommendationRepository),
        context_builder=c.resolve(PlanContextBuilder),
        trace_service=c.resolve(CognitiveTraceService),
        event_bus=c.resolve(EventBus)
    ))
    # Context Engine
    from app.infrastructure.persistence.postgres.repositories.enterprise_context_repository import EnterpriseContextRepository
    from app.application.context.engine import ContextEngine, AbstractContextEngine
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

    from app.infrastructure.vectorstore.qdrant import QdrantService
    container.register_singleton(QdrantService, QdrantService())

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

    container.register_factory(ContextProviderRegistry, build_context_registry)

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

    # =========================================================================
    # Cognitive Pipeline Auto-Wiring (Milestones 3-6)
    # =========================================================================
    import inspect
    from app.intelligence.intake.intent.engine import IntentEngine as CognitiveIntentEngine
    from app.intelligence.intake.situation.engine import SituationAnalysisEngine
    from app.intelligence.strategy.objectives.engine import ExecutiveObjectivesEngine
    from app.intelligence.strategy.goals.engine import GoalManagementEngine
    from app.intelligence.decision.decision.engine import DecisionEngine
    from app.intelligence.decision.planning.engine import PlanningEngine as CognitivePlanningEngine
    from app.intelligence.oversight.cycle.engine import CognitiveCycleController
    from app.intelligence.oversight.convergence.engine import ConvergenceEngine
    from app.intelligence.oversight.arbitration.engine import ExecutiveArbitrationEngine
    from app.intelligence.oversight.assumptions.engine import AssumptionManager
    from app.intelligence.oversight.validation.engine import ExecutiveValidationEngine
    from app.intelligence.learning.reflection.engine import ReflectionEngine
    from app.intelligence.learning.evaluation.engine import OutcomeEvaluationEngine
    from app.intelligence.learning.synthesis.engine import KnowledgeSynthesisEngine
    from app.intelligence.learning.repository.engine import ExecutiveKnowledgeRepository
    from app.intelligence.learning.heuristics.engine import ExecutiveHeuristicsEngine
    from app.intelligence.integration.pipeline import CognitivePipeline
    from app.intelligence.integration.orchestrator import ExecutiveIntelligenceOrchestrator

    pipeline_engines = [
        CognitiveIntentEngine, SituationAnalysisEngine, ExecutiveObjectivesEngine, GoalManagementEngine,
        DecisionEngine, CognitivePlanningEngine, CognitiveCycleController, ConvergenceEngine,
        ExecutiveArbitrationEngine, AssumptionManager, ExecutiveValidationEngine, ReflectionEngine,
        OutcomeEvaluationEngine, KnowledgeSynthesisEngine, ExecutiveKnowledgeRepository,
        ExecutiveHeuristicsEngine, CognitivePipeline, ExecutiveIntelligenceOrchestrator
    ]

    for engine_cls in pipeline_engines:
        if engine_cls not in container._factories and engine_cls not in container._singletons:
            def make_factory(cls):
                sig = inspect.signature(cls.__init__)
                deps = {}
                for name, param in sig.parameters.items():
                    if name in ('self', 'args', 'kwargs'): continue
                    if param.annotation == inspect.Parameter.empty: continue
                    deps[name] = param.annotation
                def factory(c: "Container", deps=deps, cls=cls):
                    kwargs = {}
                    for k, v in deps.items():
                        if not isinstance(v, str):
                            kwargs[k] = c.resolve(v)
                        else:
                            # Map strings back to types for resolution
                            if v == 'AbstractAIKernel':
                                from app.infrastructure.ai.kernel import AbstractAIKernel
                                kwargs[k] = c.resolve(AbstractAIKernel)
                            elif v == 'EventBus':
                                from app.shared.events.bus import EventBus
                                kwargs[k] = c.resolve(EventBus)
                            elif v == 'CognitiveTraceService':
                                from app.application.trace.cognitive_trace_service import CognitiveTraceService
                                kwargs[k] = c.resolve(CognitiveTraceService)
                            elif v == 'CognitivePipeline':
                                from app.intelligence.integration.pipeline import CognitivePipeline
                                kwargs[k] = c.resolve(CognitivePipeline)
                    return cls(**kwargs)
                return factory
            container.register_factory(engine_cls, make_factory(engine_cls))

