import asyncio
import pytest
from datetime import datetime, timezone
from uuid import uuid4

from app.domain.memory.models import (
    MemoryType, MemoryScope, MemoryImportance, MemoryQuery,
    WorkingMemory, EpisodicMemory, SemanticMemory, ProceduralMemory
)
from app.domain.memory.events import (
    MemoryCreated, MemoryUpdated, MemoryRemoved, MemoryRetrieved
)
from app.application.memory.service import MemoryEngineService
from app.infrastructure.memory.in_memory import InMemoryMemoryRepository

# Minimal Mock EventBus for testing
class MockEventBus:
    def __init__(self):
        self.published_events = []

    async def publish(self, event):
        self.published_events.append(event)
        
    async def subscribe(self, event_type, handler):
        pass


@pytest.fixture
def memory_service():
    repo = InMemoryMemoryRepository()
    event_bus = MockEventBus()
    return MemoryEngineService(repository=repo, event_bus=event_bus)


@pytest.mark.asyncio
async def test_memory_crud_and_events(memory_service):
    # Create
    tenant_id = uuid4()
    mem = WorkingMemory(content={"task": "Fix bug"}, tenant_id=tenant_id)
    await memory_service.save_memory(mem)
    
    events = memory_service._event_bus.published_events
    assert len(events) == 1
    assert isinstance(events[0], MemoryCreated)
    assert events[0].memory_id == mem.id
    
    # Retrieve
    retrieved = await memory_service.get_memory(mem.id, query_context="test")
    assert retrieved is not None
    assert retrieved.content["task"] == "Fix bug"
    assert len(events) == 2
    assert isinstance(events[1], MemoryRetrieved)
    assert events[1].memory_id == mem.id
    assert events[1].query_context == "test"
    
    # Update
    retrieved.importance = MemoryImportance.HIGH
    await memory_service.update_memory(retrieved)
    assert len(events) == 3
    assert isinstance(events[2], MemoryUpdated)
    assert events[2].updates["importance"] == MemoryImportance.HIGH
    
    # Remove
    await memory_service.remove_memory(mem.id)
    assert len(events) == 4
    assert isinstance(events[3], MemoryRemoved)
    assert events[3].memory_id == mem.id
    
    deleted = await memory_service.get_memory(mem.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_scope_isolation_and_querying(memory_service):
    tenant_id = uuid4()
    mem1 = EpisodicMemory(content={"event": "login"}, scope=MemoryScope.USER, tenant_id=tenant_id)
    mem2 = SemanticMemory(content={"fact": "sky is blue"}, scope=MemoryScope.GLOBAL, tenant_id=tenant_id)
    
    await memory_service.save_memory(mem1)
    await memory_service.save_memory(mem2)
    
    # Query by scope
    q1 = MemoryQuery(scopes=[MemoryScope.USER], tenant_id=tenant_id)
    res1 = await memory_service.find(q1)
    assert len(res1) == 1
    assert res1[0].id == mem1.id
    
    # Query by type
    q2 = MemoryQuery(memory_types=[MemoryType.SEMANTIC], tenant_id=tenant_id)
    res2 = await memory_service.find(q2)
    assert len(res2) == 1
    assert res2[0].id == mem2.id


@pytest.mark.asyncio
async def test_snapshot_immutability(memory_service):
    tenant_id = uuid4()
    mem1 = SemanticMemory(content={"key": "val1"}, tenant_id=tenant_id)
    await memory_service.save_memory(mem1)
    
    q = MemoryQuery(tenant_id=tenant_id)
    snapshot = await memory_service.get_snapshot(q)
    
    assert len(snapshot.records) == 1
    assert snapshot.records[0].id == mem1.id
    
    # Test immutability via Pydantic frozen config
    with pytest.raises(Exception): # ValidationError or TypeError depending on Pydantic version
        snapshot.version = 2


@pytest.mark.asyncio
async def test_batch_operations(memory_service):
    tenant_id = uuid4()
    records = [
        WorkingMemory(content={"id": 1}, tenant_id=tenant_id),
        WorkingMemory(content={"id": 2}, tenant_id=tenant_id),
        WorkingMemory(content={"id": 3}, tenant_id=tenant_id)
    ]
    
    await memory_service.batch_save(records)
    
    q = MemoryQuery(tenant_id=tenant_id)
    found = await memory_service.find(q)
    assert len(found) == 3
    
    await memory_service.batch_remove([r.id for r in records[:2]])
    
    found_after = await memory_service.find(q)
    assert len(found_after) == 1
    assert found_after[0].id == records[2].id


@pytest.mark.asyncio
async def test_entity_reference_validation(memory_service):
    entity_id = uuid4()
    mem = ProceduralMemory(
        content={"action": "run"}, 
        associated_entities=[entity_id]
    )
    await memory_service.save_memory(mem)
    
    q = MemoryQuery(associated_entities=[entity_id])
    found = await memory_service.find(q)
    assert len(found) == 1
    assert found[0].id == mem.id
    
    q2 = MemoryQuery(associated_entities=[uuid4()])
    not_found = await memory_service.find(q2)
    assert len(not_found) == 0


@pytest.mark.asyncio
async def test_concurrency(memory_service):
    # Test that asyncio locks prevent race conditions during save
    # Not a true multithreading test, but validates async task safety
    import asyncio
    
    mem = SemanticMemory(content={"test": 1})
    
    async def concurrent_save():
        await memory_service.save_memory(mem)
        
    await asyncio.gather(
        concurrent_save(),
        concurrent_save(),
        concurrent_save()
    )
    
    # Should only exist once
    q = MemoryQuery()
    results = await memory_service.find(q)
    assert len(results) == 1
