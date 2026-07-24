import pytest

from app.runtime.registry.store import InMemoryRegistryStore


@pytest.mark.asyncio
async def test_in_memory_store_crud():
    store = InMemoryRegistryStore[str]()

    # Empty
    assert await store.get("key1") is None
    assert await store.list_all() == []

    # Set
    await store.set("key1", "value1")
    assert await store.get("key1") == "value1"

    # Set another
    await store.set("key2", "value2")
    all_items = await store.list_all()
    assert len(all_items) == 2
    assert "value1" in all_items
    assert "value2" in all_items

    # Delete
    deleted = await store.delete("key1")
    assert deleted is True
    assert await store.get("key1") is None

    # Clear
    await store.clear()
    assert await store.list_all() == []
