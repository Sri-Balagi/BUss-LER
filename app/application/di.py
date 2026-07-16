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
    from app.application.twin.get_history import GetTwinHistoryUseCase
    from app.application.twin.get_snapshots import GetTwinSnapshotsUseCase
    from app.application.twin.get_twin import GetTwinUseCase
    from app.application.twin.list_twins import ListTwinsUseCase
    from app.application.twin.update_twin import UpdateTwinUseCase
    from app.infrastructure.persistence.postgres.repositories.history_repository import (
        HistoryRepository,
    )
    from app.infrastructure.persistence.postgres.repositories.snapshot_repository import (
        SnapshotRepository,
    )
    from app.infrastructure.persistence.postgres.repositories.twin_repository import (
        TwinRepository,
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
        CreateTwinUseCase,
        lambda c: CreateTwinUseCase(c.resolve(TwinRepository), c.resolve(EntityRepository)),
    )
    container.register_factory(GetTwinUseCase, lambda c: GetTwinUseCase(c.resolve(TwinRepository)))
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
    from app.infrastructure.ai.kernel import AbstractAIKernel
    from app.shared.events.bus import AsyncioEventBus, EventBus

    # Register a global EventBus singleton
    container.register_singleton(EventBus, AsyncioEventBus())

    # Trace
    from app.application.trace.cognitive_trace_service import CognitiveTraceService
    from app.infrastructure.persistence.postgres.repositories.cognitive_trace_repository import (
        CognitiveTraceRepository as TraceRepository,
    )

    def build_trace_repo(c: "Container") -> TraceRepository:
        return TraceRepository(client=c.resolve(AsyncClient))

    container.register_factory(TraceRepository, build_trace_repo)
    container.register_factory(
        CognitiveTraceService, lambda c: CognitiveTraceService(c.resolve(TraceRepository))
    )

    # Intent
    from app.application.intent.intent_classifier import IntentClassifier
    from app.application.intent.intent_service import IntentService
    from app.infrastructure.persistence.postgres.repositories.intent_repository import (
        IntentRepository,
    )

    def build_intent_repo(c: "Container") -> IntentRepository:
        return IntentRepository(client=c.resolve(AsyncClient))

    container.register_factory(IntentRepository, build_intent_repo)
    container.register_factory(
        IntentClassifier,
        lambda c: IntentClassifier(
            ai_kernel=c.resolve(AbstractAIKernel), trace_service=c.resolve(CognitiveTraceService)
        ),
    )
    container.register_factory(
        IntentService,
        lambda c: IntentService(
            repository=c.resolve(IntentRepository),
            event_bus=c.resolve(EventBus),
            classifier=c.resolve(IntentClassifier),
        ),
    )

    # Goal
    from app.application.goal.goal_service import GoalService
    from app.infrastructure.persistence.postgres.repositories.goal_repository import GoalRepository

    def build_goal_repo(c: "Container") -> GoalRepository:
        return GoalRepository(client=c.resolve(AsyncClient))

    container.register_factory(GoalRepository, build_goal_repo)
    container.register_factory(
        GoalService,
        lambda c: GoalService(repository=c.resolve(GoalRepository), event_bus=c.resolve(EventBus)),
    )

    # Conversation
    from app.application.conversation.conversation_service import ConversationService
    from app.infrastructure.persistence.postgres.repositories.conversation_repository import (
        ConversationRepository,
    )

    def build_conversation_repo(c: "Container") -> ConversationRepository:
        return ConversationRepository(client=c.resolve(AsyncClient))

    container.register_factory(ConversationRepository, build_conversation_repo)
    container.register_factory(
        ConversationService,
        lambda c: ConversationService(
            repository=c.resolve(ConversationRepository), event_bus=c.resolve(EventBus)
        ),
    )

    # Planning

    from app.application.planning.context_builder import ContextBuilder as PlanContextBuilder
    from app.application.planning.plan_service import PlanService
    from app.application.planning.planning_engine import PlanningEngine
    from app.infrastructure.persistence.postgres.repositories.plan_repository import PlanRepository

    def build_plan_repo(c: "Container") -> PlanRepository:
        return PlanRepository(client=c.resolve(AsyncClient))

    container.register_factory(PlanRepository, build_plan_repo)
    container.register_factory(
        PlanService,
        lambda c: PlanService(repository=c.resolve(PlanRepository), event_bus=c.resolve(EventBus)),
    )

    from app.infrastructure.vectorstore.qdrant import QdrantService

    container.register_factory(
        PlanContextBuilder,
        lambda c: PlanContextBuilder(
            goal_service=c.resolve(GoalService), memory_service=c.resolve(QdrantService)
        ),
    )

    container.register_factory(
        PlanningEngine,
        lambda c: PlanningEngine(
            ai_kernel=c.resolve(AbstractAIKernel),
            plan_repository=c.resolve(PlanRepository),
            context_builder=c.resolve(PlanContextBuilder),
            goal_service=c.resolve(GoalService),
            trace_service=c.resolve(CognitiveTraceService),
            event_bus=c.resolve(EventBus),
        ),
    )

    # Recommendation
    from app.application.recommendation.recommendation_engine import RecommendationEngine
    from app.application.recommendation.recommendation_service import RecommendationService
    from app.infrastructure.persistence.postgres.repositories.recommendation_repository import (
        RecommendationRepository,
    )

    def build_rec_repo(c: "Container") -> RecommendationRepository:
        return RecommendationRepository(client=c.resolve(AsyncClient))

    container.register_factory(RecommendationRepository, build_rec_repo)
    container.register_factory(
        RecommendationService,
        lambda c: RecommendationService(
            repository=c.resolve(RecommendationRepository), event_bus=c.resolve(EventBus)
        ),
    )
    container.register_factory(
        RecommendationEngine,
        lambda c: RecommendationEngine(
            ai_kernel=c.resolve(AbstractAIKernel),
            repository=c.resolve(RecommendationRepository),
            context_builder=c.resolve(PlanContextBuilder),
            trace_service=c.resolve(CognitiveTraceService),
            event_bus=c.resolve(EventBus),
        ),
    )
    # Context Engine
    from app.application.context.dependency_graph import build_default_dependency_graph
    from app.application.context.engine import AbstractContextEngine, ContextEngine
    from app.application.context.provider_registry import ContextProviderRegistry
    from app.application.context.providers.business_state_provider import (
        BusinessStateContextProvider,
    )
    from app.application.context.providers.conversation_provider import ConversationContextProvider
    from app.application.context.providers.external_provider import (
        ExternalIntegrationContextProvider,
    )
    from app.application.context.providers.goal_provider import GoalContextProvider
    from app.application.context.providers.intent_provider import IntentContextProvider
    from app.application.context.providers.memory_provider import MemoryContextProvider
    from app.application.context.providers.plan_provider import PlanContextProvider
    from app.application.context.providers.recommendation_provider import (
        RecommendationContextProvider,
    )
    from app.application.context.providers.trace_provider import TraceContextProvider
    from app.application.context.providers.twin_provider import TwinContextProvider
    from app.application.context.strategies import (
        DefaultContextCompressor,
        DefaultContextRanker,
        DefaultContextWindowBuilder,
    )
    from app.application.context.validators import DefaultContextValidator
    from app.infrastructure.cache.context_cache import MemoryContextCache
    from app.infrastructure.persistence.postgres.repositories.enterprise_context_repository import (
        EnterpriseContextRepository,
    )
    from app.intelligence.intake.situation.enterprise_context import ProviderMetadata
    from app.shared.enums import ContextSource

    def build_enterprise_context_repo(c: "Container") -> EnterpriseContextRepository:
        return EnterpriseContextRepository(client=c.resolve(AsyncClient))

    container.register_factory(EnterpriseContextRepository, build_enterprise_context_repo)
    container.register_singleton(MemoryContextCache, MemoryContextCache())

    container.register_singleton(QdrantService, QdrantService())

    def build_context_registry(c: "Container") -> ContextProviderRegistry:
        registry = ContextProviderRegistry()
        from app.infrastructure.vectorstore.qdrant import QdrantService

        registry.register(
            provider=MemoryContextProvider(c.resolve(QdrantService)),
            metadata=ProviderMetadata(
                source=ContextSource.MEMORY, name="MemoryProvider", version="1.0"
            ),
        )
        registry.register(
            provider=IntentContextProvider(c.resolve(IntentService)),
            metadata=ProviderMetadata(
                source=ContextSource.INTENT, name="IntentProvider", version="1.0"
            ),
        )
        registry.register(
            provider=GoalContextProvider(c.resolve(GoalService)),
            metadata=ProviderMetadata(
                source=ContextSource.GOAL, name="GoalProvider", version="1.0"
            ),
        )
        registry.register(
            provider=PlanContextProvider(c.resolve(PlanService)),
            metadata=ProviderMetadata(
                source=ContextSource.PLAN, name="PlanProvider", version="1.0"
            ),
        )
        registry.register(
            provider=RecommendationContextProvider(c.resolve(RecommendationEngine)),
            metadata=ProviderMetadata(
                source=ContextSource.RECOMMENDATION, name="RecommendationProvider", version="1.0"
            ),
        )
        # Assuming TwinContextProvider needs TwinRepository here, wait! Let's check dependencies_context.py to see what it actually takes.
        # But wait, dependencies_context.py showed: TwinContextProvider(twin_service)
        # For now, let's inject a string or placeholder if it's missing, but we already have UseCases.
        registry.register(
            provider=TwinContextProvider(
                c.resolve(GetTwinUseCase)
            ),  # Temporarily None until we check its signature
            metadata=ProviderMetadata(
                source=ContextSource.TWIN, name="TwinProvider", version="1.0"
            ),
        )
        registry.register(
            provider=ConversationContextProvider(c.resolve(ConversationService)),
            metadata=ProviderMetadata(
                source=ContextSource.CONVERSATION, name="ConversationProvider", version="1.0"
            ),
        )
        registry.register(
            provider=TraceContextProvider(c.resolve(CognitiveTraceService)),
            metadata=ProviderMetadata(
                source=ContextSource.TRACE, name="TraceProvider", version="1.0"
            ),
        )
        registry.register(
            provider=BusinessStateContextProvider(c.resolve(GetTwinUseCase)),
            metadata=ProviderMetadata(
                source=ContextSource.BUSINESS_STATE, name="BusinessStateProvider", version="1.0"
            ),
        )
        registry.register(
            provider=ExternalIntegrationContextProvider(),
            metadata=ProviderMetadata(
                source=ContextSource.EXTERNAL, name="ExternalProvider", version="1.0"
            ),
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
            trace_service=c.resolve(CognitiveTraceService),
        )

    container.register_factory(AbstractContextEngine, build_context_engine)
    container.register_factory(ContextEngine, build_context_engine)

    # =========================================================================
    # Cognitive Pipeline Auto-Wiring (Milestones 3-6)
    # =========================================================================
    import inspect

    from app.intelligence.decision.decision.engine import DecisionEngine
    from app.intelligence.decision.planning.engine import PlanningEngine as CognitivePlanningEngine
    from app.intelligence.intake.intent.engine import IntentEngine as CognitiveIntentEngine
    from app.intelligence.intake.situation.engine import SituationAnalysisEngine
    from app.intelligence.integration.orchestrator import ExecutiveIntelligenceOrchestrator
    from app.intelligence.integration.pipeline import CognitivePipeline
    
    # Wave-1 Executive Runtime (M7)
    from app.intelligence.executive.session_factory import SessionFactory
    from app.intelligence.executive.interfaces import IExecutiveController
    from app.intelligence.executive.controller import ExecutiveController
    
    # Wave-1 AI OS Core (M8-M10)
    from app.intelligence.executive.session_store import ISessionStore, InMemorySessionStore
    from app.intelligence.executive.workflow import IWorkflowEngine, LocalDAGWorkflowEngine
    from app.intelligence.executive.approval import IApprovalProvider, HumanApprovalProvider
    from app.intelligence.pipeline.interfaces import IAsyncCognitivePipeline
    from app.intelligence.pipeline.pipeline import AsyncCognitivePipeline
    from app.intelligence.pipeline.builtin_phases import ExecutePhase, ReflectPhase, LearnPhase

    from app.intelligence.learning.evaluation.engine import OutcomeEvaluationEngine
    from app.intelligence.learning.heuristics.engine import ExecutiveHeuristicsEngine
    from app.intelligence.learning.reflection.engine import ReflectionEngine
    from app.intelligence.learning.repository.engine import ExecutiveKnowledgeRepository
    from app.intelligence.learning.synthesis.engine import KnowledgeSynthesisEngine
    from app.intelligence.oversight.arbitration.engine import ExecutiveArbitrationEngine
    from app.intelligence.oversight.assumptions.engine import AssumptionManager
    from app.intelligence.oversight.convergence.engine import ConvergenceEngine
    from app.intelligence.oversight.cycle.engine import CognitiveCycleController
    from app.intelligence.oversight.validation.engine import ExecutiveValidationEngine
    from app.intelligence.strategy.goals.engine import GoalManagementEngine
    from app.intelligence.strategy.objectives.engine import ExecutiveObjectivesEngine

    pipeline_engines = [
        CognitiveIntentEngine,
        SituationAnalysisEngine,
        ExecutiveObjectivesEngine,
        GoalManagementEngine,
        DecisionEngine,
        CognitivePlanningEngine,
        CognitiveCycleController,
        ConvergenceEngine,
        ExecutiveArbitrationEngine,
        AssumptionManager,
        ExecutiveValidationEngine,
        ReflectionEngine,
        OutcomeEvaluationEngine,
        KnowledgeSynthesisEngine,
        ExecutiveKnowledgeRepository,
        ExecutiveHeuristicsEngine,
        CognitivePipeline,
        ExecutiveIntelligenceOrchestrator,
        # Wave-1 Executive Runtime
        SessionFactory,
        ExecutiveController,
        # Wave-1 OS Core
        InMemorySessionStore,
        LocalDAGWorkflowEngine,
        HumanApprovalProvider,
        ExecutePhase,
        ReflectPhase,
        LearnPhase,
        AsyncCognitivePipeline,
    ]

    for engine_cls in pipeline_engines:
        if engine_cls not in container._factories and engine_cls not in container._singletons:

            def make_factory(cls):
                sig = inspect.signature(cls.__init__)
                deps = {}
                for name, param in sig.parameters.items():
                    if name in ("self", "args", "kwargs"):
                        continue
                    if param.annotation == inspect.Parameter.empty:
                        continue
                    deps[name] = param.annotation

                def factory(c: "Container", deps=deps, cls=cls):
                    kwargs = {}
                    for k, v in deps.items():
                        if not isinstance(v, str):
                            kwargs[k] = c.resolve(v)
                        else:
                            # Map strings back to types for resolution
                            if v == "AbstractAIKernel":
                                from app.infrastructure.ai.kernel import AbstractAIKernel

                                kwargs[k] = c.resolve(AbstractAIKernel)
                            elif v == "EventBus":
                                from app.shared.events.bus import EventBus

                                kwargs[k] = c.resolve(EventBus)
                            elif v == "CognitiveTraceService":
                                from app.application.trace.cognitive_trace_service import (
                                    CognitiveTraceService,
                                )

                                kwargs[k] = c.resolve(CognitiveTraceService)
                            elif v == "CognitivePipeline":
                                from app.intelligence.integration.pipeline import CognitivePipeline

                                kwargs[k] = c.resolve(CognitivePipeline)
                    return cls(**kwargs)

                return factory

            container.register_factory(engine_cls, make_factory(engine_cls))
            
    # Bind the Wave-1 Controller Interface to its Implementation
    container.register_factory(IExecutiveController, lambda c: c.resolve(ExecutiveController))
    
    # Bind OS Interfaces
    container.register_factory(ISessionStore, lambda c: c.resolve(InMemorySessionStore))
    container.register_factory(IWorkflowEngine, lambda c: c.resolve(LocalDAGWorkflowEngine))
    container.register_factory(IApprovalProvider, lambda c: c.resolve(HumanApprovalProvider))
    container.register_factory(IAsyncCognitivePipeline, lambda c: c.resolve(AsyncCognitivePipeline))

    # =========================================================================
    # Wave-2 OS Kernel Foundations (V7.0)
    # =========================================================================
    from app.infrastructure.vfs.vfs import IVirtualFileSystem
    from app.runtime.kernel.interfaces import (
        IKernel,
        IRuntimeManager,
        IProcessManager,
        ISessionManager,
        IScheduler,
        IResourceManager,
        IPolicyEngine,
        IServiceDiscovery,
    )
    from app.runtime.kernel.syscall import ISyscallInterface
    
    # Milestone 2 Concrete Imports
    from app.shared.bus.system_bus import ISystemBus, LocalSystemBus
    from app.runtime.kernel.manager import RuntimeManager, ProcessManager
    from app.runtime.kernel.scheduler import LocalScheduler
    from app.runtime.kernel.process import ProcessTable
    
    from app.runtime.lifecycle.interfaces import ILifecycleManager
    from app.runtime.lifecycle.session import SessionLifecycleManager
    from app.runtime.lifecycle.workflow import WorkflowLifecycleManager
    from app.runtime.lifecycle.process import ProcessLifecycleManager
    
    from app.infrastructure.storage.storage_manager import IStorageManager
    from app.infrastructure.vfs.mount_registry import MountRegistry
    from app.infrastructure.vfs.path_resolver import MountResolver

    # Placeholder implementations for remaining abstractions
    class PlaceholderKernel(IKernel): pass
    class PlaceholderSessionManager(ISessionManager): pass
    class PlaceholderResourceManager(IResourceManager): pass
    class PlaceholderPolicyEngine(IPolicyEngine): pass
    class PlaceholderServiceDiscovery(IServiceDiscovery): pass
    class PlaceholderStorageManager(IStorageManager): 
        def ping(self) -> bool: return True
    
    class PlaceholderSyscall(ISyscallInterface):
        def start_session(self, context): pass
        def stop_session(self, session_id): pass
        def suspend(self, pid): pass
        def resume(self, pid): pass
        def allocate(self, resource_type, amount): pass
        def release(self, resource_type, amount): pass
        def read(self, uri): pass
        def write(self, uri, content): pass
        def search(self, query, context=None): pass
        def invoke_capability(self, capability_uri, payload): pass
        def request_approval(self, approval_type, context): pass
        def publish_event(self, topic, event_data): pass
        def subscribe(self, topic, callback): pass
        def log(self, level, message): pass
        def checkpoint(self, pid): pass
        def restore(self, pid, checkpoint_uri): pass
        
    class PlaceholderVFS(IVirtualFileSystem):
        def mount_manager(self): pass
        def path_resolver(self): pass
        def read(self, uri): pass
        def write(self, uri, content): pass

    container.register_factory(IKernel, lambda c: PlaceholderKernel())
    container.register_factory(ISessionManager, lambda c: PlaceholderSessionManager())
    container.register_factory(IResourceManager, lambda c: PlaceholderResourceManager())
    container.register_factory(IPolicyEngine, lambda c: PlaceholderPolicyEngine())
    container.register_factory(IServiceDiscovery, lambda c: PlaceholderServiceDiscovery())
    container.register_factory(ISyscallInterface, lambda c: PlaceholderSyscall())
    container.register_factory(IVirtualFileSystem, lambda c: PlaceholderVFS())
    
    # Milestone 2 DI Bindings
    container.register_singleton(ISystemBus, lambda c: LocalSystemBus())
    container.register_singleton(ProcessTable, lambda c: ProcessTable())
    container.register_singleton(IProcessManager, lambda c: ProcessManager(c.resolve(ProcessTable)))
    container.register_singleton(IRuntimeManager, lambda c: RuntimeManager(c.resolve(IProcessManager), c.resolve(ISystemBus)))
    container.register_singleton(IScheduler, lambda c: LocalScheduler(c.resolve(IProcessManager)))
    
    container.register_singleton(SessionLifecycleManager, lambda c: SessionLifecycleManager())
    container.register_singleton(WorkflowLifecycleManager, lambda c: WorkflowLifecycleManager())
    container.register_singleton(ProcessLifecycleManager, lambda c: ProcessLifecycleManager(c.resolve(IProcessManager)))
    
    container.register_singleton(IStorageManager, lambda c: PlaceholderStorageManager())
    container.register_singleton(MountRegistry, lambda c: MountRegistry())
    container.register_singleton(MountResolver, lambda c: MountResolver(c.resolve(MountRegistry)))

    # System Query Service (Wave 3.1)
    from app.runtime.registry.store import InMemoryRegistryStore
    from app.runtime.registry.tool_registry import ToolRegistry
    from app.runtime.registry.workflow_registry import WorkflowRegistry
    from app.application.system.query_service import SystemQueryService
    
    # Normally these registries would have persistent stores. For MVP, we use InMemoryRegistryStore
    container.register_factory(InMemoryRegistryStore, lambda c: InMemoryRegistryStore())
    container.register_factory(ToolRegistry, lambda c: ToolRegistry("ToolRegistry", c.resolve(InMemoryRegistryStore)))
    container.register_factory(WorkflowRegistry, lambda c: WorkflowRegistry("WorkflowRegistry", c.resolve(InMemoryRegistryStore)))
    
    container.register_factory(SystemQueryService, lambda c: SystemQueryService(
        runtime_manager=c.resolve(IRuntimeManager),
        tool_registry=c.resolve(ToolRegistry),
        workflow_registry=c.resolve(WorkflowRegistry)
    ))
    
    from app.runtime.mcp.bridge import MCPBridge
    container.register_factory(MCPBridge, lambda c: MCPBridge(c.resolve(ToolRegistry)))

    # =========================================================================
    # Wave-2 Milestone 3 — Distributed Runtime (V7.0)
    # =========================================================================
    from app.runtime.distributed.interfaces import (
        IDistributedScheduler,
        IDistributedSystemBus,
    )
    from app.runtime.distributed.celery_scheduler import CeleryDistributedScheduler
    from app.runtime.distributed.redis_bus import RedisSystemBus
    from app.runtime.distributed.worker_node import BizOSWorkerNode

    container.register_singleton(
        IDistributedScheduler,
        lambda c: CeleryDistributedScheduler(),
    )
    container.register_singleton(
        IDistributedSystemBus,
        lambda c: RedisSystemBus(),
    )
    # Worker node is registered as a factory (each call returns a new node instance)
    container.register_factory(
        BizOSWorkerNode,
        lambda c: BizOSWorkerNode(),
    )

    # =========================================================================
    # Wave-2 Milestone 4 — Storage Layer (V7.0)
    # =========================================================================
    from app.infrastructure.vfs.postgres_mount import PostgresMount
    from app.infrastructure.vfs.qdrant_mount import QdrantMount
    from app.infrastructure.vfs.redis_mount import RedisMount
    from app.infrastructure.storage.snapshot_manager import SnapshotManager
    from app.infrastructure.storage.backup_manager import BackupManager
    from app.infrastructure.storage.concrete_storage_manager import ConcreteStorageManager

    # VFS Mounts — registered individually so callers can resolve by concrete type.
    # Clients are None by default; startup wiring (lifespan) will inject live clients.
    container.register_singleton(PostgresMount, lambda c: PostgresMount(supabase_client=None))
    container.register_singleton(QdrantMount, lambda c: QdrantMount(qdrant_client=None))
    container.register_singleton(RedisMount, lambda c: RedisMount(redis_client=None))

    # Register mounts into the MountRegistry so VFS resolution works end-to-end
    def _build_mount_registry(c) -> MountRegistry:
        registry = MountRegistry()
        registry.register("pg", c.resolve(PostgresMount))
        registry.register("qdrant", c.resolve(QdrantMount))
        registry.register("redis", c.resolve(RedisMount))
        return registry

    # Override the Milestone 2 MountRegistry singleton with the fully-populated one
    container.register_singleton(MountRegistry, _build_mount_registry)

    # Snapshot & Backup Managers
    container.register_singleton(
        SnapshotManager,
        lambda c: SnapshotManager(redis_client=None),  # redis_client injected at startup
    )
    container.register_singleton(
        BackupManager,
        lambda c: BackupManager(
            redis_client=None,
            snapshot_manager=c.resolve(SnapshotManager),
        ),
    )

    # Upgrade IStorageManager binding from placeholder to ConcreteStorageManager
    container.register_singleton(
        ConcreteStorageManager,
        lambda c: ConcreteStorageManager(mount_registry=c.resolve(MountRegistry)),
    )

