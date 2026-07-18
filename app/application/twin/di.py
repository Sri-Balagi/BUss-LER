from app.bootstrap.container import Container
from app.domain.intelligence.provider import ICapabilityRegistry
from app.application.twin.service import DigitalTwinService
from app.application.twin.orchestrator import TwinSyncOrchestrator
from app.domain.twin.sync import ITwinSynchronizer, RealTimeSynchronization
from app.infrastructure.twin.in_memory import InMemoryTwinProvider
from app.application.intelligence.kernel import IntelligenceKernel


def register_twin_dependencies(container: Container) -> None:
    """Wire Digital Twin dependencies and register with Capability Registry."""
    
    # Register the Sync Strategy
    container.register_factory(
        ITwinSynchronizer,
        lambda c: RealTimeSynchronization()
    )
    
    # Register the Twin Service
    container.register_factory(
        DigitalTwinService,
        lambda c: DigitalTwinService(capability_registry=c.resolve(ICapabilityRegistry))
    )
    
    # Register Orchestrator
    container.register_factory(
        TwinSyncOrchestrator,
        lambda c: TwinSyncOrchestrator(
            synchronizer=c.resolve(ITwinSynchronizer),
            twin_service=c.resolve(DigitalTwinService),
            kernel=c.resolve(IntelligenceKernel)
        )
    )
    
    # Register Provider to the Capability Registry
    def _register_provider(c: Container) -> InMemoryTwinProvider:
        provider = InMemoryTwinProvider()
        registry = c.resolve(ICapabilityRegistry)
        registry.register_provider(provider)
        return provider
        
    container.register_factory(InMemoryTwinProvider, _register_provider)
    
    # Eagerly instantiate to register it immediately
    _register_provider(container)
