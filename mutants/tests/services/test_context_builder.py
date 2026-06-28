import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.services.context_builder import ContextBuilder
from app.models.context import CognitiveContext
from app.models.exceptions import ContextBuildError
from app.models.intent import Intent
from app.core.context import OperationContext


@pytest.fixture
def mock_goal_service():
    service = AsyncMock()
    service.get_active_goals.return_value = []
    return service


@pytest.fixture
def mock_memory_service():
    service = AsyncMock()
    service.search_memories = AsyncMock()
    return service


@pytest.fixture
def op_ctx():
    return OperationContext(correlation_id="test-corr-id")


@pytest.mark.asyncio
async def test_build_success_without_intent(
    mock_goal_service, mock_memory_service, op_ctx
):
    twin_id = uuid4()

    mock_goal_service.get_active_goals.return_value = []

    builder = ContextBuilder(
        goal_service=mock_goal_service, memory_service=mock_memory_service
    )

    context = await builder.build(ctx=op_ctx, twin_id=twin_id)

    assert isinstance(context, CognitiveContext)
    assert context.twin_id == twin_id
    assert context.current_intent is None
    assert context.active_goals == []
    assert context.relevant_memories == []
    assert context.goal_ids_used == []
    assert context.memory_ids_used == []
    assert context.estimated_token_count == 0


@pytest.mark.asyncio
async def test_build_success_with_intent(
    mock_goal_service, mock_memory_service, op_ctx
):
    twin_id = uuid4()
    intent = MagicMock(spec=Intent)
    intent.raw_text = "Test intent"

    mock_goal_service.get_active_goals.return_value = []

    mock_search_result = MagicMock()
    mock_item = MagicMock()
    mock_item.memory.id = uuid4()
    mock_item.memory.content = "Memory content"
    mock_item.similarity_score = 0.95
    mock_item.memory.memory_category.value = "test_cat"
    mock_search_result.items = [mock_item]
    mock_memory_service.search_memories.return_value = mock_search_result

    builder = ContextBuilder(
        goal_service=mock_goal_service, memory_service=mock_memory_service
    )

    context = await builder.build(ctx=op_ctx, twin_id=twin_id, intent=intent)

    assert context.current_intent == intent
    assert len(context.relevant_memories) == 1
    assert context.relevant_memories[0].memory_id == mock_item.memory.id
    assert context.relevant_memories[0].content == "Memory content"
    assert context.relevant_memories[0].similarity_score == 0.95
    assert context.memory_ids_used == [mock_item.memory.id]

    mock_memory_service.search_memories.assert_called_once()
    args, kwargs = mock_memory_service.search_memories.call_args
    assert args[1].query_text == "Test intent"
    assert args[1].twin_id == twin_id


@pytest.mark.asyncio
async def test_build_handles_memory_exception(
    mock_goal_service, mock_memory_service, op_ctx
):
    twin_id = uuid4()
    intent = MagicMock(spec=Intent)
    intent.raw_text = "Test"

    mock_goal_service.get_active_goals.return_value = []
    mock_memory_service.search_memories.side_effect = Exception("Search failed")

    builder = ContextBuilder(
        goal_service=mock_goal_service, memory_service=mock_memory_service
    )

    context = await builder.build(ctx=op_ctx, twin_id=twin_id, intent=intent)

    assert context.relevant_memories == []
    assert context.memory_ids_used == []
    assert context.estimated_token_count == 0


@pytest.mark.asyncio
async def test_build_raises_exception_on_goal_error(
    mock_goal_service, mock_memory_service, op_ctx
):
    twin_id = uuid4()

    mock_goal_service.get_active_goals.side_effect = Exception("DB failure")

    builder = ContextBuilder(
        goal_service=mock_goal_service, memory_service=mock_memory_service
    )

    with pytest.raises(ContextBuildError):
        await builder.build(ctx=op_ctx, twin_id=twin_id)
