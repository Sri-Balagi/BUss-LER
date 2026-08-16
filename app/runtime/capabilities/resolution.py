from abc import ABC, abstractmethod

from app.runtime.capabilities.interfaces import ICapabilityFactory
from app.runtime.capabilities.models.resolution import (
    CapabilityResolutionContext,
    CapabilityResolutionDecision,
)
from app.runtime.capabilities.models.specification import CapabilitySpecification


class ICapabilityResolutionStrategy(ABC):
    @abstractmethod
    def resolve(
        self,
        context: CapabilityResolutionContext,
        candidates: list[tuple[CapabilitySpecification, ICapabilityFactory]],
    ) -> CapabilityResolutionDecision:
        pass


class ExactMatchStrategy(ICapabilityResolutionStrategy):
    def resolve(
        self,
        context: CapabilityResolutionContext,
        candidates: list[tuple[CapabilitySpecification, ICapabilityFactory]],
    ) -> CapabilityResolutionDecision:
        for spec, factory in candidates:
            if spec.capability_id == context.capability_id and (
                not context.requested_version or spec.version == context.requested_version
            ):
                return CapabilityResolutionDecision(
                    selected_factory=factory,
                    selected_specification=spec,
                    version_resolution=spec.version,
                    selection_reason="Exact match strategy success",
                )
        raise ValueError(
            f"No exact match found for {context.capability_id} v{context.requested_version}"
        )


class NewestCompatibleStrategy(ICapabilityResolutionStrategy):
    def resolve(
        self,
        context: CapabilityResolutionContext,
        candidates: list[tuple[CapabilitySpecification, ICapabilityFactory]],
    ) -> CapabilityResolutionDecision:
        valid_candidates = [
            (spec, factory)
            for spec, factory in candidates
            if spec.capability_id == context.capability_id
        ]

        if not valid_candidates:
            raise ValueError(f"No compatible candidates found for {context.capability_id}")

        # Simplified sort by version string
        valid_candidates.sort(key=lambda x: x[0].version, reverse=True)
        best_spec, best_factory = valid_candidates[0]

        return CapabilityResolutionDecision(
            selected_factory=best_factory,
            selected_specification=best_spec,
            version_resolution=best_spec.version,
            selection_reason="Newest compatible version selected",
        )
