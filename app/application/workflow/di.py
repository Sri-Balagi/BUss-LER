from app.bootstrap.container import Container
from app.application.intelligence.kernel import IntelligenceKernel
from app.domain.intelligence.provider import ICapabilityRegistry
from app.application.workflow.steps.optimization_step import WorkflowOptimizationStep
from app.application.workflow.service import WorkflowIntelligenceService
from app.infrastructure.workflow.mock_provider import MockWorkflowIntelligenceProvider


def configure_workflow_intelligence(container: Container) -> None:
    """Configures the Workflow Intelligence dependencies."""
    
    # 1. Register the step
    container.register_factory(
        WorkflowOptimizationStep,
        lambda c: WorkflowOptimizationStep(
            registry=c.resolve(ICapabilityRegistry),
            event_router=c.resolve(IntelligenceKernel).event_router
        )
    )
    
    # 2. Register the service
    container.register_factory(
        WorkflowIntelligenceService,
        lambda c: WorkflowIntelligenceService(
            pipeline_manager=c.resolve(IntelligenceKernel).pipeline_manager,
            optimization_step=c.resolve(WorkflowOptimizationStep)
        )
    )
    
    # 3. Register the Mock Provider via ICapabilityRegistry
    def register_mock_workflow_provider(c: Container):
        registry = c.resolve(ICapabilityRegistry)
        mock_provider = MockWorkflowIntelligenceProvider(priority=1, name="MockWorkflowOptimizer")
        registry.register_provider(mock_provider)
        return registry
        
    container.register_factory(
        "workflow_registry_initializer",
        register_mock_workflow_provider
    )
