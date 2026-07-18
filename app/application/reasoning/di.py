from app.bootstrap.container import Container
from app.application.reasoning.pipeline import ReasoningPipeline
from app.application.reasoning.service import ReasoningEngineService
from app.domain.intelligence.provider import ICapabilityRegistry
from app.application.twin.service import DigitalTwinService
from app.application.intelligence.kernel import IntelligenceKernel
from app.infrastructure.reasoning.mock_provider import MockReasoningProvider


def register_reasoning_dependencies(container: Container) -> None:
    """Wire Reasoning Layer dependencies."""
    
    # Register Pipeline
    container.register_factory(
        ReasoningPipeline,
        lambda c: ReasoningPipeline(
            capability_registry=c.resolve(ICapabilityRegistry),
            twin_service=c.resolve(DigitalTwinService),
            event_router=c.resolve(IntelligenceKernel).event_router
        )
    )
    
    # Register Service
    container.register_factory(
        ReasoningEngineService,
        lambda c: ReasoningEngineService(
            kernel=c.resolve(IntelligenceKernel),
            pipeline=c.resolve(ReasoningPipeline)
        )
    )
    
    # Register Mock Provider
    def _register_mock_provider(c: Container) -> MockReasoningProvider:
        provider = MockReasoningProvider(priority=1, name="MockReasoningProvider")
        registry = c.resolve(ICapabilityRegistry)
        registry.register_provider(provider)
        return provider
        
    container.register_factory(MockReasoningProvider, _register_mock_provider)
    
    # Eagerly instantiate to register
    _register_mock_provider(container)
