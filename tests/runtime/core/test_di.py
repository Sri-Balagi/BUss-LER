import pytest

from app.bootstrap.container import build_container, get_container, reset_container_for_testing
from app.config import Settings
from app.infrastructure.ai.budgets.interfaces import IResourceBudget
from app.infrastructure.ai.kernel import AbstractAIKernel, AIKernel
from app.infrastructure.ai.observability.metrics import ProviderObserver
from app.infrastructure.ai.prompts.registry import PromptRegistry
from app.infrastructure.ai.providers.base import ILLMProvider
from app.infrastructure.ai.registry import ProviderRegistry
from app.infrastructure.ai.router import ProviderRouter
from app.infrastructure.execution.factory import ExecutionStrategyFactory
from app.infrastructure.execution.strategy import IExecutionStrategy


@pytest.fixture(autouse=True)
def container():
    reset_container_for_testing()
    # Provide a mock env for Settings so we don't need real keys
    import os

    os.environ["GEMINI_API_KEY"] = "mock-key-for-testing-123"
    os.environ["SUPABASE_URL"] = "http://mock.supabase.co"
    os.environ["SUPABASE_KEY"] = "mock-supabase-key-12345"

    c = build_container()
    yield c
    reset_container_for_testing()


def test_dependency_graph_validation(container):
    """
    Validates the entire Provider Platform dependency graph.
    - AIKernel requires no manual construction.
    - The graph is fully connected.
    - The graph is acyclic.
    """

    # Resolving AIKernel should recursively build all dependencies without RecursionError
    kernel = container.resolve(AIKernel)
    assert isinstance(kernel, AIKernel)

    # Resolving AbstractAIKernel should return the exact same type of instance
    kernel2 = container.resolve(AbstractAIKernel)
    assert isinstance(kernel2, AIKernel)

    # 1. Check AIKernel dependencies are properly wired
    assert hasattr(kernel, "_router")
    assert hasattr(kernel, "_prompt_manager")
    assert hasattr(kernel, "_budget")

    # 2. Verify Singletons remain Singletons
    prompt_registry1 = container.resolve(PromptRegistry)
    prompt_registry2 = container.resolve(PromptRegistry)
    assert prompt_registry1 is prompt_registry2
    assert kernel._prompt_manager is prompt_registry1

    budget1 = container.resolve(IResourceBudget)
    budget2 = container.resolve(IResourceBudget)
    assert budget1 is budget2
    assert kernel._budget is budget1

    # 3. Check Provider Router and Default Provider
    router = container.resolve(ProviderRouter)
    assert router is kernel._router

    # The default provider in the router should be "gemini"
    assert router._default_provider == "gemini"
    default_provider = container.resolve(ILLMProvider)
    assert router.get_active_provider() is default_provider

    # 4. Check ProviderObserver is applied
    assert isinstance(default_provider, ProviderObserver)
    assert default_provider.provider_name == "gemini"

    # 5. Check Registry contains the observed provider
    registry = container.resolve(ProviderRegistry)
    gemini_from_registry = registry.get_provider("gemini")
    assert gemini_from_registry is default_provider


def test_execution_strategy_wiring(container):
    """Verifies Execution Strategy wiring."""
    strategy = container.resolve(IExecutionStrategy)
    factory = container.resolve(ExecutionStrategyFactory)

    assert strategy is not None
    assert factory is not None


def test_settings_wiring(container):
    """Verifies Configuration Services wiring."""
    settings = container.resolve(Settings)
    assert settings is not None
    assert settings.gemini_api_key == "mock-key-for-testing-123"
