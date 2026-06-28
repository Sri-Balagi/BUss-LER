import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.models.enums import ContextSource
from app.services.context_policies import ContextPolicy
from app.services.context_providers.memory_provider import MemoryContextProvider
from app.services.context_providers.goal_provider import GoalContextProvider
from app.models.enterprise_context import ContextItem

@pytest.mark.asyncio
async def test_memory_provider_success():
    mock_service = AsyncMock()
    mock_result = MagicMock()
    
    # Setup mock items
    mock_memory_item = MagicMock()
    mock_memory_item.memory.id = uuid4()
    mock_memory_item.memory.content = "Test memory content"
    mock_memory_item.similarity_score = 0.95
    
    mock_result.items = [mock_memory_item]
    mock_service.search_memories.return_value = mock_result
    
    provider = MemoryContextProvider(memory_service=mock_service)
    policy = ContextPolicy(
        policy_id="test",
        name="Test",
        enabled_providers=[ContextSource.MEMORY],
        max_memories=5
    )
    
    section = await provider.provide(ctx=MagicMock(), twin_id=uuid4(), policy=policy)
    
    assert section.source == ContextSource.MEMORY
    assert len(section.items) == 1
    item: ContextItem = section.items[0]
    
    assert item.content == "Test memory content"
    assert item.provenance.provider == ContextSource.MEMORY
    assert item.provenance.confidence == 0.95
    assert item.domain_object_id == mock_memory_item.memory.id

@pytest.mark.asyncio
async def test_memory_provider_exception_handling():
    mock_service = AsyncMock()
    mock_service.search_memories.side_effect = Exception("Service unavailable")
    
    provider = MemoryContextProvider(memory_service=mock_service)
    policy = ContextPolicy(
        policy_id="test",
        name="Test",
        enabled_providers=[ContextSource.MEMORY]
    )
    
    # Should not raise exception, should return empty section
    section = await provider.provide(ctx=MagicMock(), twin_id=uuid4(), policy=policy)
    
    assert section.source == ContextSource.MEMORY
    assert len(section.items) == 0

@pytest.mark.asyncio
async def test_goal_provider_success():
    mock_service = AsyncMock()
    
    # Setup mock goals
    mock_goal = MagicMock()
    mock_goal.id = uuid4()
    mock_goal.title = "Increase revenue"
    mock_goal.description = "Q3 targets"
    mock_goal.status.value = "active"
    mock_goal.priority.value = "high"
    
    mock_service.get_active_goals.return_value = [mock_goal]
    
    provider = GoalContextProvider(goal_service=mock_service)
    policy = ContextPolicy(
        policy_id="test",
        name="Test",
        enabled_providers=[ContextSource.GOAL],
        max_goals=3
    )
    
    section = await provider.provide(ctx=MagicMock(), twin_id=uuid4(), policy=policy)
    
    assert section.source == ContextSource.GOAL
    assert len(section.items) == 1
    item: ContextItem = section.items[0]
    
    assert "Increase revenue" in item.content
    assert "Q3 targets" in item.content
    assert item.provenance.provider == ContextSource.GOAL
    assert item.domain_object_id == mock_goal.id

@pytest.mark.asyncio
async def test_goal_provider_exception_handling():
    mock_service = AsyncMock()
    mock_service.get_active_goals.side_effect = Exception("Service unavailable")
    
    provider = GoalContextProvider(goal_service=mock_service)
    policy = ContextPolicy(
        policy_id="test",
        name="Test",
        enabled_providers=[ContextSource.GOAL]
    )
    
    # Should not raise exception, should return empty section
    section = await provider.provide(ctx=MagicMock(), twin_id=uuid4(), policy=policy)
    
    assert section.source == ContextSource.GOAL
    assert len(section.items) == 0
