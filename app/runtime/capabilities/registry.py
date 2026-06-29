from typing import List, Tuple, Optional
from app.runtime.capabilities.interfaces import ICapabilityFactory
from app.runtime.capabilities.models.specification import CapabilitySpecification
from app.runtime.capabilities.models.resolution import CapabilityResolutionContext, CapabilityResolutionDecision
from app.runtime.capabilities.resolution import ICapabilityResolutionStrategy, ExactMatchStrategy

class CapabilityRegistry:
    def __init__(self, default_strategy: ICapabilityResolutionStrategy = None):
        self._capabilities: List[Tuple[CapabilitySpecification, ICapabilityFactory]] = []
        self.default_strategy = default_strategy or ExactMatchStrategy()
        
    def register(self, spec: CapabilitySpecification, factory: ICapabilityFactory) -> None:
        self._capabilities.append((spec, factory))
        
    def unregister(self, capability_id: str, version: Optional[str] = None) -> None:
        self._capabilities = [
            (s, f) for s, f in self._capabilities 
            if not (s.capability_id == capability_id and (not version or s.version == version))
        ]
        
    def resolve(
        self, 
        context: CapabilityResolutionContext, 
        strategy: ICapabilityResolutionStrategy = None
    ) -> CapabilityResolutionDecision:
        active_strategy = strategy or self.default_strategy
        return active_strategy.resolve(context, self._capabilities)
        
    def enumerate(self) -> List[CapabilitySpecification]:
        return [spec for spec, _ in self._capabilities]
