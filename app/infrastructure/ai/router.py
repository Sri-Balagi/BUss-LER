from collections.abc import Callable
from enum import StrEnum
from typing import Any

from app.infrastructure.ai.models import ProviderError
from app.infrastructure.ai.observability.metrics import LLM_FALLBACK_ACTIVATIONS
from app.infrastructure.ai.providers.base import ILLMProvider
from app.infrastructure.ai.registry import ProviderRegistry


class RoutingPolicy(StrEnum):
    PRIMARY_WITH_FALLBACK = "primary_with_fallback"
    COST_FIRST = "cost_first"
    LATENCY_FIRST = "latency_first"
    QUALITY_FIRST = "quality_first"
    JSON_RELIABLE_FIRST = "json_first"


class CapabilityNotAvailableError(Exception):
    """Raised when no provider can satisfy the requested capability constraints."""
    pass


class ProviderRouter:
    """
    Routes AI requests to the appropriate provider based on capabilities and semantics.
    """

    def __init__(
        self,
        registry: ProviderRegistry,
        default_provider: str = "gemini",
        fallback_provider: str | None = None,
        routing_policy: RoutingPolicy = RoutingPolicy.PRIMARY_WITH_FALLBACK
    ):
        self._registry = registry
        self._default_provider = default_provider
        self._fallback_provider = fallback_provider
        self._routing_policy = routing_policy

    def get_active_provider(
        self, requested_provider: str | None = None
    ) -> ILLMProvider:
        """
        Backward-compatible method. Returns requested or default provider.
        """
        provider_name = requested_provider or self._default_provider
        return self._registry.get_provider(provider_name)

    def get_provider_for_capability(
        self,
        required_capability: str,
        preferred_provider: str | None = None,
        min_json_reliability: float | None = None,
        min_reasoning_quality: float | None = None
    ) -> ILLMProvider:
        """Return the best available provider for the required capability."""

        # 1. If provider explicitly requested and registered -> use it
        if preferred_provider:
            return self._registry.get_provider(preferred_provider)

        eligible_providers = self._registry.list_providers()

        # 2. Filter by required technical capability
        eligible_providers = [
            p for p in eligible_providers
            if getattr(p.capabilities, required_capability, False)
        ]

        # 3. Filter by minimum semantic capability score (if specified)
        if min_json_reliability is not None:
            eligible_providers = [
                p for p in eligible_providers
                if getattr(p.capabilities, "json_reliability", 0.0) >= min_json_reliability
            ]

        if min_reasoning_quality is not None:
            eligible_providers = [
                p for p in eligible_providers
                if getattr(p.capabilities, "reasoning_quality", 0.0) >= min_reasoning_quality
            ]

        if not eligible_providers:
            raise CapabilityNotAvailableError(
                f"No provider found satisfying capability '{required_capability}' "
                f"and semantic requirements."
            )

        # 4. Apply RoutingPolicy to select from eligible set
        if self._routing_policy == RoutingPolicy.COST_FIRST:
            tier_weights = {"budget": 1, "medium": 2, "premium": 3, "ultra": 4}
            return min(
                eligible_providers,
                key=lambda p: tier_weights.get(getattr(p.capabilities, "cost_tier", "medium"), 2)
            )

        elif self._routing_policy == RoutingPolicy.LATENCY_FIRST:
            tier_weights = {"fast": 1, "medium": 2, "slow": 3}
            return min(
                eligible_providers,
                key=lambda p: tier_weights.get(getattr(p.capabilities, "latency_tier", "medium"), 2)
            )

        elif self._routing_policy == RoutingPolicy.QUALITY_FIRST:
            return max(
                eligible_providers,
                key=lambda p: getattr(p.capabilities, "reasoning_quality", 0.0)
            )

        elif self._routing_policy == RoutingPolicy.JSON_RELIABLE_FIRST:
            return max(
                eligible_providers,
                key=lambda p: getattr(p.capabilities, "json_reliability", 0.0)
            )

        # PRIMARY_WITH_FALLBACK or unhandled policy
        return self.get_active_provider()

    async def route_with_fallback(
        self,
        primary: ILLMProvider,
        operation: Callable,
        *args, **kwargs
    ) -> Any:
        """
        Execute operation on primary; retry on fallback on ProviderError.
        """
        try:
            return await operation(primary, *args, **kwargs)
        except ProviderError as e:
            if not self._fallback_provider:
                raise e

            try:
                fallback = self._registry.get_provider(self._fallback_provider)
            except Exception:
                # If fallback isn't registered, just raise the original error
                raise e

            # Record fallback activation metric
            LLM_FALLBACK_ACTIVATIONS.labels(
                primary_provider=primary.provider_name,
                fallback_provider=fallback.provider_name
            ).inc()

            # Execute on fallback. If this raises, it will bubble up.
            return await operation(fallback, *args, **kwargs)
