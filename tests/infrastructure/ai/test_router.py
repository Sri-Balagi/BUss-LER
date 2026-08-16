import asyncio
from collections.abc import AsyncIterator
from typing import Any

import pytest

from app.infrastructure.ai.models import ProviderError
from app.infrastructure.ai.observability.metrics import LLM_FALLBACK_ACTIVATIONS
from app.infrastructure.ai.providers.mock.provider import MockLLMProvider
from app.infrastructure.ai.providers.mock.scenarios import MockScenarioConfig, MockScenarioMode
from app.infrastructure.ai.registry import ProviderRegistry
from app.infrastructure.ai.router import CapabilityNotAvailableError, ProviderRouter, RoutingPolicy


@pytest.fixture
def mock_registry():
    registry = ProviderRegistry()

    # Primary Mock Provider
    primary = MockLLMProvider("gemini")
    primary.capabilities.supports_streaming = True
    primary.capabilities.supports_structured_output = True
    primary.capabilities.json_reliability = 0.95
    primary.capabilities.reasoning_quality = 0.9
    primary.capabilities.latency_tier = "medium"
    primary.capabilities.cost_tier = "premium"

    # Secondary Mock Provider (Fallback)
    fallback = MockLLMProvider("openai")
    fallback.capabilities.supports_streaming = False
    fallback.capabilities.supports_structured_output = True
    fallback.capabilities.json_reliability = 0.5
    fallback.capabilities.reasoning_quality = 0.7
    fallback.capabilities.latency_tier = "fast"
    fallback.capabilities.cost_tier = "medium"

    # Tertiary Mock Provider
    tertiary = MockLLMProvider("anthropic")
    tertiary.capabilities.supports_streaming = True
    tertiary.capabilities.supports_structured_output = False
    tertiary.capabilities.json_reliability = 0.6
    tertiary.capabilities.reasoning_quality = 0.95
    tertiary.capabilities.latency_tier = "slow"
    tertiary.capabilities.cost_tier = "ultra"

    registry.register(primary)
    registry.register(fallback)
    registry.register(tertiary)

    return registry


@pytest.fixture
def router(mock_registry):
    return ProviderRouter(
        registry=mock_registry,
        default_provider="gemini",
        fallback_provider="openai",
        routing_policy=RoutingPolicy.PRIMARY_WITH_FALLBACK,
    )


def test_default_routing_returns_gemini_provider(router):
    provider = router.get_active_provider()
    assert provider.provider_name == "gemini"


def test_capability_filter_excludes_providers_without_supports_streaming(router):
    provider = router.get_provider_for_capability("supports_streaming")
    # Both gemini and anthropic support streaming. gemini is default.
    assert provider.provider_name == "gemini"

    # If we change policy to latency first
    router._routing_policy = RoutingPolicy.LATENCY_FIRST
    # fast provider (openai) is excluded because it doesn't support streaming.
    # Between medium (gemini) and slow (anthropic), gemini wins
    p = router.get_provider_for_capability("supports_streaming")
    assert p.provider_name == "gemini"


def test_min_json_reliability_excludes_providers(router):
    provider = router.get_provider_for_capability(
        "supports_structured_output", min_json_reliability=0.9
    )
    # openai has 0.5 json_reliability, anthropic doesn't support structured output
    assert provider.provider_name == "gemini"

    # If we request JSON reliability > 0.99, no one satisfies
    with pytest.raises(CapabilityNotAvailableError):
        router.get_provider_for_capability("supports_structured_output", min_json_reliability=0.99)


def test_capability_not_available_error(router):
    with pytest.raises(CapabilityNotAvailableError):
        router.get_provider_for_capability("supports_vision")


@pytest.mark.asyncio
async def test_fallback_routing(router, mock_registry):
    primary = mock_registry.get_provider("gemini")
    mock_registry.get_provider("openai")

    # Configure primary to fail
    primary.configure_scenario(
        MockScenarioConfig(mode=MockScenarioMode.FAILURE_SIMULATION, fail_on_call=1)
    )

    async def mock_operation(p, *args, **kwargs):
        if p.provider_name == "gemini":
            raise ProviderError("gemini", "test_op", "simulated failure")
        return "fallback_success"

    result = await router.route_with_fallback(primary, mock_operation)
    assert result == "fallback_success"


@pytest.mark.asyncio
async def test_double_failure_re_raises_fallback_error(router, mock_registry):
    primary = mock_registry.get_provider("gemini")
    mock_registry.get_provider("openai")

    # Configure both to fail
    async def mock_operation(p, *args, **kwargs):
        raise ProviderError(p.provider_name, "test_op", "simulated failure")

    with pytest.raises(ProviderError) as exc_info:
        await router.route_with_fallback(primary, mock_operation)

    assert exc_info.value.provider == "openai"


@pytest.mark.asyncio
async def test_llm_fallback_activations_increments(router, mock_registry):
    primary = mock_registry.get_provider("gemini")
    mock_registry.get_provider("openai")

    initial_count = LLM_FALLBACK_ACTIVATIONS.labels(
        primary_provider="gemini", fallback_provider="openai"
    )._value.get()

    async def mock_operation(p, *args, **kwargs):
        if p.provider_name == "gemini":
            raise ProviderError("gemini", "test_op", "simulated failure")
        return "fallback_success"

    await router.route_with_fallback(primary, mock_operation)

    final_count = LLM_FALLBACK_ACTIVATIONS.labels(
        primary_provider="gemini", fallback_provider="openai"
    )._value.get()

    assert final_count == initial_count + 1


def test_routing_policies(mock_registry):
    # Cost First
    r_cost = ProviderRouter(mock_registry, routing_policy=RoutingPolicy.COST_FIRST)
    p = r_cost.get_provider_for_capability("supports_structured_output")
    assert p.provider_name == "openai"  # medium tier (gemini is premium)

    # Latency First
    r_latency = ProviderRouter(mock_registry, routing_policy=RoutingPolicy.LATENCY_FIRST)
    p = r_latency.get_provider_for_capability("supports_structured_output")
    assert p.provider_name == "openai"  # fast tier

    # Quality First
    r_quality = ProviderRouter(mock_registry, routing_policy=RoutingPolicy.QUALITY_FIRST)
    # Anthropic has reasoning_quality=0.95, gemini=0.9, openai=0.7
    # But let's check supports_streaming since anthropic doesn't support structured_output
    p = r_quality.get_provider_for_capability("supports_streaming")
    assert p.provider_name == "anthropic"

    # JSON Reliable First
    r_json = ProviderRouter(mock_registry, routing_policy=RoutingPolicy.JSON_RELIABLE_FIRST)
    p = r_json.get_provider_for_capability("supports_structured_output")
    assert p.provider_name == "gemini"  # 0.95 vs 0.5
