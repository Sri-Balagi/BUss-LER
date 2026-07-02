from app.runtime.capabilities.interfaces import ICapabilityFactory
from app.runtime.capabilities.models.resolution import (
    CapabilityResolutionContext,
    CapabilityResolutionDecision,
)
from app.runtime.capabilities.models.specification import CapabilitySpecification
from app.runtime.capabilities.resolution import ExactMatchStrategy, ICapabilityResolutionStrategy


class CapabilityRegistry:
    def __init__(self, default_strategy: ICapabilityResolutionStrategy = None):
        self._capabilities: list[tuple[CapabilitySpecification, ICapabilityFactory]] = []
        self.default_strategy = default_strategy or ExactMatchStrategy()

    def register(self, spec: CapabilitySpecification, factory: ICapabilityFactory) -> None:
        self._capabilities.append((spec, factory))

    def unregister(self, capability_id: str, version: str | None = None) -> None:
        self._capabilities = [
            (s, f)
            for s, f in self._capabilities
            if not (s.capability_id == capability_id and (not version or s.version == version))
        ]

    def resolve(
        self, context: CapabilityResolutionContext, strategy: ICapabilityResolutionStrategy = None
    ) -> CapabilityResolutionDecision:
        active_strategy = strategy or self.default_strategy
        return active_strategy.resolve(context, self._capabilities)

    def enumerate(self) -> list[CapabilitySpecification]:
        return [spec for spec, _ in self._capabilities]
