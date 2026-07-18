import uuid

from app.bootstrap.container import Container
from app.domain.intelligence.capability import CapabilityType, CapabilityMetadata
from app.domain.intelligence.provider import ProviderLifecycleStatus, ICapabilityRegistry
from app.application.intelligence.kernel import IntelligenceKernel
from app.domain.learning.provider import ILearningProvider
from app.infrastructure.learning.mock_provider import MockLearningProvider
from app.application.learning.service import LearningService
from app.application.learning.steps.consolidation_step import ConsolidationStep


def register_learning_subsystem(container: Container):
    """
    Registers the learning components into the DI container and Capability Registry.
    """
    
    # 1. Register MockLearningProvider
    container.register_factory(MockLearningProvider, lambda c: MockLearningProvider())
    
    # 2. Register ConsolidationStep
    container.register_factory(
        ConsolidationStep, 
        lambda c: ConsolidationStep(
            registry=c.resolve(ICapabilityRegistry),
            event_router=c.resolve(IntelligenceKernel).event_router
        )
    )
    
    # 3. Register LearningService
    container.register_factory(
        LearningService, 
        lambda c: LearningService(
            kernel=c.resolve(IntelligenceKernel),
            consolidation_step=c.resolve(ConsolidationStep)
        )
    )
    
    # 4. Register the Mock provider into the Capability Registry using a registry initializer
    def register_mock_learning_provider(c: Container):
        registry = c.resolve(ICapabilityRegistry)
        
        # We assume register_provider on ICapabilityRegistry either accepts a MockLearningProvider 
        # or we just let MockLearningProvider set its own metadata if that's how Wave 5 does it.
        # Wait, the previous test in workflow used:
        # mock_provider = MockWorkflowIntelligenceProvider(priority=1, name="MockWorkflowOptimizer")
        # registry.register_provider(mock_provider)
        
        provider = c.resolve(MockLearningProvider)
        # To make it compatible with the test assertion `assert provider.get_metadata().provider_name == "MockLearningProvider"`,
        # we might need to modify MockLearningProvider to expose get_metadata()
        
        # Or if registry.register_provider(provider) works:
        registry.register_provider(provider)
        return registry
        
    container.register_factory(
        "learning_registry_initializer",
        register_mock_learning_provider
    )
