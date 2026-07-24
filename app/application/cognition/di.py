from app.application.cognition.pipeline import CognitivePipeline
from app.application.cognition.service import CognitiveEngineService
from app.application.cognition.steps.execute_step import ExecuteStep
from app.application.cognition.steps.observe_step import ObserveStep
from app.application.cognition.steps.plan_step import PlanStep
from app.application.cognition.steps.reason_step import ReasonStep
from app.application.cognition.steps.reflect_step import ReflectStep
from app.application.cognition.steps.retrieve_step import RetrieveStep
from app.application.intelligence.kernel import IntelligenceKernel
from app.bootstrap.container import Container
from app.domain.intelligence.provider import ICapabilityRegistry
from app.infrastructure.cognition.mock_provider import MockAgentImplementation


def configure_cognition_dependencies(container: Container) -> None:
    """Register all Agent Cognition components in the DI container."""

    # 1. Register Steps
    container.register_factory(ObserveStep, lambda c: ObserveStep())
    container.register_factory(RetrieveStep, lambda c: RetrieveStep())
    container.register_factory(ReasonStep, lambda c: ReasonStep())
    container.register_factory(PlanStep, lambda c: PlanStep())
    container.register_factory(ExecuteStep, lambda c: ExecuteStep())

    container.register_factory(
        ReflectStep,
        lambda c: ReflectStep(event_router=c.resolve(IntelligenceKernel).event_router)
    )

    # 2. Register Pipeline
    container.register_factory(
        CognitivePipeline,
        lambda c: CognitivePipeline(
            steps=[
                c.resolve(ObserveStep),
                c.resolve(RetrieveStep),
                c.resolve(ReasonStep),
                c.resolve(PlanStep),
                c.resolve(ExecuteStep),
                c.resolve(ReflectStep),
            ],
            event_router=c.resolve(IntelligenceKernel).event_router,
            max_iterations=5,
            max_execution_time=60.0
        )
    )

    # 3. Register Service
    container.register_factory(
        CognitiveEngineService,
        lambda c: CognitiveEngineService(
            kernel=c.resolve(IntelligenceKernel),
            pipeline=c.resolve(CognitivePipeline)
        )
    )

    # 4. Register Mock Provider via ICapabilityRegistry
    def register_mock_agent(c: Container):
        registry = c.resolve(ICapabilityRegistry)
        mock_provider = MockAgentImplementation(priority=1, name="DefaultAgent")
        registry.register_provider(mock_provider)
        return registry

    # We'll just execute this to populate the registry at bootstrap
    container.register_factory(
        "cognition_registry_initializer",
        register_mock_agent
    )
