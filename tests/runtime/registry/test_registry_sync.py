from typing import Any

import pytest
from pydantic import BaseModel

from app.runtime.registry.base import BaseRegistry
from app.runtime.registry.store import InMemoryRegistryStore
from app.runtime.registry.sync import RegistrySnapshot


class DummyItem(BaseModel):
    id: str
    name: str

class DummyRegistry(BaseRegistry[DummyItem]):
    def _deserialize_item(self, data: dict[str, Any]) -> DummyItem:
        return DummyItem.model_validate(data)

@pytest.mark.asyncio
async def test_export_import_snapshot():
    store1 = InMemoryRegistryStore[DummyItem]()
    registry1 = DummyRegistry("Dummy", store1)

    await registry1.register("1", DummyItem(id="1", name="One"))
    await registry1.register("2", DummyItem(id="2", name="Two"))

    snapshot = await registry1.export_snapshot()
    assert snapshot.registry_name == "Dummy"
    assert len(snapshot.items) == 2

    json_data = snapshot.to_json()
    assert "One" in json_data

    # Import into a new registry
    store2 = InMemoryRegistryStore[DummyItem]()
    registry2 = DummyRegistry("Dummy", store2)

    new_snapshot = RegistrySnapshot.from_json(json_data)
    await registry2.import_snapshot(new_snapshot)

    items = await registry2.list_all()
    assert len(items) == 2
    names = [i.name for i in items]
    assert "One" in names
    assert "Two" in names
