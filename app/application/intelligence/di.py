from app.bootstrap.container import Container
from app.shared.events.bus import EventBus
from app.domain.intelligence.provider import ICapabilityRegistry
from app.application.intelligence.registry import CapabilityRegistryService
from app.application.intelligence.kernel import IntelligenceKernel


def register_intelligence_infrastructure(container: Container) -> None:
    """Register the foundational Intelligence Domain dependencies."""
    
    # Registry is a global singleton
    container.register_singleton(
        ICapabilityRegistry,
        CapabilityRegistryService()
    )
    
    # Kernel requires the EventBus
    def _kernel_factory(c: Container) -> IntelligenceKernel:
        return IntelligenceKernel(event_bus=c.resolve(EventBus))
        
    container.register_factory(IntelligenceKernel, _kernel_factory)
    
    # Register the unified platform
    from app.domain.intelligence.platform import IIntelligencePlatform
    from app.application.intelligence.platform import UnifiedIntelligencePlatform
    
    def _platform_factory(c: Container) -> IIntelligencePlatform:
        from app.application.intelligence.providers import (
            GeminiProvider, OpenAIProvider, ClaudeProvider, OllamaProvider, CognitiveSimulatorProvider
        )
        providers = {
            "gemini": GeminiProvider(),
            "openai": OpenAIProvider(),
            "claude": ClaudeProvider(),
            "ollama": OllamaProvider(),
            "simulator": CognitiveSimulatorProvider()
        }
        return UnifiedIntelligencePlatform(
            kernel=c.resolve(IntelligenceKernel),
            registry=c.resolve(ICapabilityRegistry),
            providers=providers,
            default_provider="simulator",
            fallback_providers=["openai", "gemini"]
        )
        
    container.register_factory(IIntelligencePlatform, _platform_factory)
