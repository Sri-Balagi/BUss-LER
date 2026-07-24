import asyncio
from typing import Any

import pytest
from pydantic import BaseModel

from app.runtime.registry.base import BaseRegistry
from app.runtime.registry.registry_bus import IRegistryBus
from app.runtime.registry.store import InMemoryRegistryStore


class DummyItem(BaseModel):
    id: str
    name: str

class DummyRegistry(BaseRegistry[DummyItem]):
    def _deserialize_item(self, data: dict[str, Any]) -> DummyItem:
        return DummyItem.model_validate(data)

class DummyBus(IRegistryBus):
    def __init__(self):
        self.events = []
    async def publish_event(self, topic: str, payload: dict[str, Any]) -> None:
        self.events.append((topic, payload))

@pytest.fixture
def store():
    return InMemoryRegistryStore[DummyItem]()

@pytest.fixture
def bus():
    return DummyBus()

@pytest.fixture
def registry(store, bus):
    return DummyRegistry("DummyRegistry", store, bus)

@pytest.mark.asyncio
async def test_register_and_get(registry):
    item = DummyItem(id="item-1", name="Test Item")
    await registry.register(item.id, item)

    retrieved = await registry.get("item-1")
    assert retrieved is not None
    assert retrieved.name == "Test Item"

    assert len(registry.bus.events) == 1
    assert registry.bus.events[0][0] == "registry.DummyRegistry.registered"

@pytest.mark.asyncio
async def test_unregister(registry):
    item = DummyItem(id="item-2", name="Test Item 2")
    await registry.register(item.id, item)

    success = await registry.unregister("item-2")
    assert success is True

    retrieved = await registry.get("item-2")
    assert retrieved is None

    assert len(registry.bus.events) == 2
    assert registry.bus.events[1][0] == "registry.DummyRegistry.unregistered"
