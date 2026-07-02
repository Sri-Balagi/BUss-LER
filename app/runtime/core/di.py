"""Dependency Injection wiring for the Execution Kernel."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.bootstrap.container import Container


def register_platform_dependencies(container: "Container") -> None:
    """
    Hooks the runtime subsystem interfaces into the global DI container.
    Constructs the acyclic dependency graph for the Provider Platform.
    """
    from app.config import Settings, get_settings
    from app.infrastructure.ai.budgets.interfaces import IResourceBudget
    from app.infrastructure.ai.budgets.token_budget_service import TokenBudgetService
    from app.infrastructure.ai.kernel import AbstractAIKernel, AIKernel
    from app.infrastructure.ai.observability.metrics import ProviderObserver
    from app.infrastructure.ai.prompts.registry import PromptRegistry
    from app.infrastructure.ai.providers.base import ILLMProvider
    from app.infrastructure.ai.providers.gemini.provider import GeminiProvider
    from app.infrastructure.ai.registry import ProviderRegistry
    from app.infrastructure.ai.router import ProviderRouter
    from app.infrastructure.execution.factory import ExecutionStrategyFactory
    from app.infrastructure.execution.in_process import InProcessExecutionStrategy
    from app.infrastructure.execution.strategy import IExecutionStrategy

    # 1. Configuration
    container.register_factory(Settings, lambda c: get_settings())

    # 2. Prompts
    container.register_singleton(PromptRegistry, PromptRegistry())

    # 3. Budgets
    container.register_singleton(IResourceBudget, TokenBudgetService())

    # 4. Providers
    # Factory for ProviderRegistry to ensure it gets correctly observed providers
    def build_provider_registry(c: "Container") -> ProviderRegistry:
        settings = c.resolve(Settings)
        # Note: In production we'd want to handle multiple providers, but Wave 0 only fully supports Gemini
        gemini = GeminiProvider(settings=settings)
        observed_gemini = ProviderObserver(gemini)

        registry = ProviderRegistry()
        registry.register(observed_gemini)
        return registry

    container.register_factory(ProviderRegistry, build_provider_registry)

    # We also register the default ILLMProvider directly, which is useful for the Router
    def build_default_provider(c: "Container") -> ILLMProvider:
        registry = c.resolve(ProviderRegistry)
        return registry.get_provider("gemini")

    container.register_factory(ILLMProvider, build_default_provider)

    # 5. Router
    def build_router(c: "Container") -> ProviderRouter:
        return ProviderRouter(
            registry=c.resolve(ProviderRegistry), default_provider="gemini", fallback_provider=None
        )

    container.register_factory(ProviderRouter, build_router)

    # 6. Kernel
    def build_kernel(c: "Container") -> AIKernel:
        return AIKernel(
            router=c.resolve(ProviderRouter),
            prompt_manager=c.resolve(PromptRegistry),
            budget=c.resolve(IResourceBudget),
        )

    container.register_factory(AbstractAIKernel, build_kernel)
    container.register_factory(AIKernel, build_kernel)

    # 7. Execution Strategy
    container.register_singleton(IExecutionStrategy, InProcessExecutionStrategy())

    def build_execution_strategy_factory(c: "Container") -> ExecutionStrategyFactory:
        # In a real DI setup with multiple strategies, the factory might take the container to resolve them.
        # But for Wave 0, the factory just creates them or we can just register the factory itself.
        return ExecutionStrategyFactory()

    container.register_factory(ExecutionStrategyFactory, build_execution_strategy_factory)
