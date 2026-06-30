from typing import Type

from app.runtime.capabilities.adapters.base import IResourceAdapter
from app.runtime.capabilities.interfaces import ICapability, ICapabilityFactory
from app.runtime.capabilities.models.specification import CapabilitySpecification


class TransientCapabilityFactory(ICapabilityFactory):
    """
    Creates a new instance of a capability and its adapter on every request.
    """
    def __init__(self, capability_cls: type[ICapability], adapter_cls: type[IResourceAdapter]):
        self.capability_cls = capability_cls
        self.adapter_cls = adapter_cls

    def create(self, spec: CapabilitySpecification) -> ICapability:
        adapter = self.adapter_cls()
        return self.capability_cls(spec=spec, adapter=adapter)

class SingletonCapabilityFactory(ICapabilityFactory):
    """
    Reuses a single instance of a capability and adapter across multiple requests.
    """
    def __init__(self, capability_cls: type[ICapability], adapter_cls: type[IResourceAdapter]):
        self.capability_cls = capability_cls
        self.adapter_cls = adapter_cls
        self._instance = None

    def create(self, spec: CapabilitySpecification) -> ICapability:
        if self._instance is None:
            adapter = self.adapter_cls()
            self._instance = self.capability_cls(spec=spec, adapter=adapter)
        return self._instance
