from app.application.intelligence.kernel import IntelligenceKernel
from app.application.reasoning.pipeline import ReasoningPipeline
from app.application.reasoning.service import ReasoningEngineService
from app.application.twin.service import DigitalTwinService
from app.bootstrap.container import Container
from app.domain.intelligence.provider import ICapabilityRegistry
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

    # Register Semantic Provider
    from app.infrastructure.reasoning.semantic_provider import SemanticReasoningProvider
    def _register_semantic_provider(c: Container) -> SemanticReasoningProvider:
        provider = SemanticReasoningProvider(priority=2, name="SemanticReasoningProvider")
        registry = c.resolve(ICapabilityRegistry)
        registry.register_provider(provider)
        return provider

    container.register_factory(SemanticReasoningProvider, _register_semantic_provider)

    # Register Gemini LLM Provider
    from app.infrastructure.reasoning.gemini_provider import GeminiReasoningProvider
    from app.config import get_settings
    
    def _register_gemini_provider(c: Container) -> GeminiReasoningProvider:
        provider = GeminiReasoningProvider(priority=3, name="GeminiReasoningProvider")
        # Only register if it initialized successfully (e.g. API key present)
        from app.domain.intelligence.provider import ProviderLifecycleStatus
        if provider.get_status() != ProviderLifecycleStatus.UNAVAILABLE:
            registry = c.resolve(ICapabilityRegistry)
            registry.register_provider(provider)
        return provider
        
    container.register_factory(GeminiReasoningProvider, _register_gemini_provider)

    # Eagerly instantiate to register
    _register_mock_provider(container)
    _register_semantic_provider(container)
    _register_gemini_provider(container)
