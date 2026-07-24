from app.application.applications.copilot.app import CopilotApplication
from app.application.applications.policy.engine import ApplicationPolicyEngine
from app.application.applications.prompt.service import PromptOrchestrationService
from app.application.applications.registry.service import ApplicationRegistryService
from app.bootstrap.container import Container
from app.domain.applications.policy.interfaces import IApplicationPolicyEngine
from app.domain.applications.prompt.interfaces import IPromptBuilder
from app.domain.applications.registry.interfaces import IApplicationRegistry
from app.domain.intelligence.platform import IIntelligencePlatform


def register_application_services(container: Container) -> None:
    """Register all Wave 6 Application services."""
    registry = ApplicationRegistryService()
    container.register_singleton(IApplicationRegistry, registry)
    container.register_singleton(IApplicationPolicyEngine, ApplicationPolicyEngine())
    container.register_singleton(IPromptBuilder, PromptOrchestrationService())

    # We use a factory for Copilot Application so it resolves IIntelligencePlatform lazily
    def copilot_factory(c: Container) -> CopilotApplication:
        platform = c.resolve(IIntelligencePlatform)
        app = CopilotApplication(platform)
        # Self-register into the registry
        registry.register(app)
        return app

    container.register_factory(CopilotApplication, copilot_factory)

    # Worker Application Dependencies
    from app.application.applications.insights.app import InsightsGenerationApplication
    from app.application.applications.worker.app import AutonomousWorkerApplication
    from app.domain.applications.worker.interfaces import IJobScheduler, IJobStore
    from app.infrastructure.applications.worker.scheduler import LocalJobScheduler
    from app.infrastructure.applications.worker.store import InMemoryJobStore
    from app.shared.events.bus import EventBus

    # The job store is a singleton
    container.register_singleton(IJobStore, InMemoryJobStore())

    # We use a factory for LocalJobScheduler to get the store and registry
    def scheduler_factory(c: Container) -> IJobScheduler:
        store = c.resolve(IJobStore)
        # We use the registry variable we created above
        return LocalJobScheduler(store, registry)

    container.register_factory(IJobScheduler, scheduler_factory)

    # Factory for the worker app itself
    def worker_factory(c: Container) -> AutonomousWorkerApplication:
        platform = c.resolve(IIntelligencePlatform)
        store = c.resolve(IJobStore)
        scheduler = c.resolve(IJobScheduler)

        app = AutonomousWorkerApplication(platform, store, scheduler)
        registry.register(app)
        return app

    container.register_factory(AutonomousWorkerApplication, worker_factory)

    # Factory for the insights app
    def insights_factory(c: Container) -> InsightsGenerationApplication:
        platform = c.resolve(IIntelligencePlatform)
        store = c.resolve(IJobStore)
        scheduler = c.resolve(IJobScheduler)
        event_bus = c.resolve(EventBus)

        app = InsightsGenerationApplication(platform, store, scheduler, event_bus)
        registry.register(app)
        return app

    container.register_factory(InsightsGenerationApplication, insights_factory)

    # Factory for the trigger engine
    from app.application.applications.trigger.app import CognitiveTriggerEngine
    from app.application.applications.trigger.evaluators import ConditionEvaluatorRegistry

    container.register_singleton(ConditionEvaluatorRegistry, ConditionEvaluatorRegistry())

    def trigger_engine_factory(c: Container) -> CognitiveTriggerEngine:
        platform = c.resolve(IIntelligencePlatform)
        store = c.resolve(IJobStore)
        scheduler = c.resolve(IJobScheduler)
        event_bus = c.resolve(EventBus)

        app = CognitiveTriggerEngine(
            platform=platform,
            app_registry=registry,
            store=store,
            scheduler=scheduler,
            event_bus=event_bus,
        )
        registry.register(app)
        return app

    container.register_factory(CognitiveTriggerEngine, trigger_engine_factory)
