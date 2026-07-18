from app.bootstrap.container import Container
from app.domain.intelligence.provider import ICapabilityRegistry
from app.application.intelligence.kernel import IntelligenceKernel
from app.domain.planning.validator import IPlanValidator
from app.application.planning.validator import DefaultPlanValidator
from app.application.planning.pipeline import PlanningPipeline
from app.application.planning.service import PlanningEngineService
from app.infrastructure.planning.deterministic_provider import DeterministicPlanningProvider


def register_planning_dependencies(container: Container) -> None:
    """Registers Planning Engine dependencies in the container."""
    
    # Register validator
    container.register_factory(IPlanValidator, lambda c: DefaultPlanValidator())
    
    # Register pipeline
    def _build_pipeline(c: Container) -> PlanningPipeline:
        return PlanningPipeline(
            registry=c.resolve(ICapabilityRegistry),
            validator=c.resolve(IPlanValidator),
            event_router=c.resolve(IntelligenceKernel).event_router
        )
    container.register_factory(PlanningPipeline, _build_pipeline)
    
    # Register service
    def _build_service(c: Container) -> PlanningEngineService:
        return PlanningEngineService(
            kernel=c.resolve(IntelligenceKernel),
            pipeline=c.resolve(PlanningPipeline)
        )
    container.register_factory(PlanningEngineService, _build_service)
    
    # Register the deterministic provider with the registry
    _register_providers(container)


def _register_providers(c: Container) -> None:
    registry = c.resolve(ICapabilityRegistry)
    provider = DeterministicPlanningProvider(priority=1, name="DefaultDeterministicPlanner")
    registry.register_provider(provider)
