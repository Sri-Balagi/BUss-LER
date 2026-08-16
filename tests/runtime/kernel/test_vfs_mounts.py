from typing import Any

import pytest

from app.infrastructure.vfs.mount_registry import MountRegistry
from app.infrastructure.vfs.path_resolver import MountResolver
from app.infrastructure.vfs.vfs import IVirtualMount, IVirtualNode


class DummyNode(IVirtualNode):
    path: str = "twin://123/memory"
    metadata: dict = {}

    def read(self) -> Any:
        return "data"

    def write(self, content: Any) -> None:
        pass

class DummyMount(IVirtualMount):
    @property
    def scheme(self) -> str:
        return "twin"

    def resolve(self, uri: str) -> IVirtualNode:
        return DummyNode()

def test_mount_registry_and_resolver():
    registry = MountRegistry()
    mount = DummyMount()
    registry.register("twin", mount)

    assert registry.get_mount("twin") is mount

    resolver = MountResolver(registry)
    node = resolver.resolve("twin://123/memory")
    assert node.read() == "data"

    with pytest.raises(ValueError):
        resolver.resolve("unknown://123/data")
