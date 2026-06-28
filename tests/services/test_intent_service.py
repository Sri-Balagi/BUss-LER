import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.services.intent_service import IntentService
from app.models.commands import (
    CreateIntentCommand,
    ClassifyIntentCommand,
    UpdateIntentStatusCommand,
    DeleteIntentCommand,
)
from app.models.enums import IntentStatus, IntentType, IntentConfidence
from app.models.intent import Intent, IntentUpdate, PaginatedIntents, IntentAnalysis
from app.models.queries import IntentListQuery
from app.models.events import IntentCreatedEvent, IntentClassifiedEvent
from app.core.context import OperationContext


@pytest.fixture
def mock_repo():
    return AsyncMock()


@pytest.fixture
def mock_event_bus():
    return AsyncMock()


@pytest.fixture
def mock_classifier():
    return AsyncMock()


@pytest.fixture
def op_ctx():
    return OperationContext(correlation_id="test-corr-id")


@pytest.fixture
def service(mock_repo, mock_event_bus, mock_classifier):
    return IntentService(
        repository=mock_repo, event_bus=mock_event_bus, classifier=mock_classifier
    )


@pytest.fixture
def mock_intent():
    intent = MagicMock(spec=Intent)
    intent.id = uuid4()
    intent.twin_id = uuid4()
    intent.raw_text = "I need to increase revenue"
    intent.status = IntentStatus.PENDING
    return intent


@pytest.mark.asyncio
async def test_create_intent(service, mock_repo, mock_event_bus, op_ctx, mock_intent):
    mock_repo.create.return_value = mock_intent
    cmd = CreateIntentCommand(
        twin_id=mock_intent.twin_id,
        raw_text="I need to increase revenue",
    )

    result = await service.create_intent(op_ctx, cmd)

    assert result.intent == mock_intent
    assert result.dispatched_events == 1

    mock_repo.create.assert_called_once()
    mock_event_bus.publish.assert_called_once()
    event = mock_event_bus.publish.call_args[0][0]
    assert isinstance(event, IntentCreatedEvent)
    assert event.intent_id == mock_intent.id


@pytest.mark.asyncio
async def test_classify_intent_success(
    service, mock_repo, mock_event_bus, mock_classifier, op_ctx, mock_intent
):
    mock_repo.get_by_id.return_value = mock_intent

    analysis = IntentAnalysis(
        intent_type=IntentType.GENERAL,
        confidence=IntentConfidence.HIGH,
        business_domain="Sales",
        primary_goal="increase revenue",
        entities=[{"value": "revenue"}],
        timeframe=None,
        reasoning_metadata={"key_signals": ["revenue"]},
    )

    mock_classify_result = MagicMock()
    mock_classify_result.analysis = analysis
    mock_classify_result.cognitive_trace = None
    mock_classifier.classify.return_value = mock_classify_result

    updated_intent = MagicMock(spec=Intent)
    updated_intent.id = mock_intent.id
    updated_intent.twin_id = mock_intent.twin_id
    updated_intent.status = IntentStatus.CLASSIFIED
    mock_repo.update.return_value = updated_intent

    cmd = ClassifyIntentCommand(intent_id=mock_intent.id, twin_id=mock_intent.twin_id)

    result = await service.classify_intent(op_ctx, cmd)

    assert result.intent == updated_intent
    assert result.analysis == analysis

    mock_repo.get_by_id.assert_called_once_with(mock_intent.id)
    mock_classifier.classify.assert_called_once_with(op_ctx, mock_intent)
    mock_repo.update.assert_called_once()

    args = mock_repo.update.call_args[0]
    assert args[0] == mock_intent.id
    assert isinstance(args[1], IntentUpdate)
    assert args[1].status == IntentStatus.CLASSIFIED
    assert args[1].intent_type == IntentType.GENERAL

    mock_event_bus.publish.assert_called_once()
    event = mock_event_bus.publish.call_args[0][0]
    assert isinstance(event, IntentClassifiedEvent)


@pytest.mark.asyncio
async def test_classify_intent_missing_classifier(
    mock_repo, mock_event_bus, op_ctx, mock_intent
):
    service_no_classifier = IntentService(
        repository=mock_repo, event_bus=mock_event_bus, classifier=None
    )

    cmd = ClassifyIntentCommand(intent_id=mock_intent.id, twin_id=mock_intent.twin_id)

    with pytest.raises(ValueError, match="IntentClassifier dependency not injected"):
        await service_no_classifier.classify_intent(op_ctx, cmd)


@pytest.mark.asyncio
async def test_get_intent(service, mock_repo, op_ctx, mock_intent):
    mock_repo.get_by_id.return_value = mock_intent

    result = await service.get_intent(op_ctx, mock_intent.id)

    assert result == mock_intent
    mock_repo.get_by_id.assert_called_once_with(mock_intent.id)


@pytest.mark.asyncio
async def test_list_intents(service, mock_repo, op_ctx):
    mock_repo.list_by_twin.return_value = PaginatedIntents(
        items=[], total_count=0, limit=10, offset=0
    )
    query = IntentListQuery(twin_id=uuid4(), limit=10, offset=0)

    result = await service.list_intents(op_ctx, query)

    assert result.total_count == 0
    mock_repo.list_by_twin.assert_called_once()


@pytest.mark.asyncio
async def test_update_intent_status(service, mock_repo, op_ctx, mock_intent):
    mock_intent.status = IntentStatus.CLASSIFIED
    mock_repo.get_by_id.return_value = mock_intent

    active_intent = MagicMock(spec=Intent)
    active_intent.id = mock_intent.id
    mock_repo.update.return_value = active_intent

    cmd = UpdateIntentStatusCommand(
        intent_id=mock_intent.id, target_status=IntentStatus.CONFIRMED
    )
    result = await service.update_intent_status(op_ctx, cmd)

    assert result == active_intent
    mock_repo.update.assert_called_once()
    args = mock_repo.update.call_args[0]
    assert args[0] == mock_intent.id
    assert args[1].status == IntentStatus.CONFIRMED


@pytest.mark.asyncio
async def test_delete_intent(service, mock_repo, op_ctx):
    cmd = DeleteIntentCommand(intent_id=uuid4())

    await service.delete_intent(op_ctx, cmd)

    mock_repo.soft_delete.assert_called_once_with(cmd.intent_id)
