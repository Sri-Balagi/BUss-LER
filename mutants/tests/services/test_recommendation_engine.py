from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from app.models.ai import AIResponseMetadata, ClassifyResponse
from app.models.commands import GenerateRecommendationsCommand
from app.models.exceptions import AIOutputValidationError, RecommendationGenerationError
from app.models.recommendation import Recommendation
from app.models.results import GenerateRecommendationsResult
from app.services.recommendation_engine import RecommendationEngine

from app.core.context import OperationContext


@pytest.fixture
def mock_ai_kernel():
    return AsyncMock()


@pytest.fixture
def mock_repo():
    return AsyncMock()


@pytest.fixture
def mock_context_engine():
    return AsyncMock()


@pytest.fixture
def mock_trace_service():
    return AsyncMock()


@pytest.fixture
def mock_event_bus():
    return AsyncMock()


@pytest.fixture
def op_ctx():
    return OperationContext(correlation_id="test-corr-id")


@pytest.fixture
def dummy_command():
    return GenerateRecommendationsCommand(twin_id=uuid4(), intent_id=uuid4())


@pytest.mark.asyncio
async def test_generate_recommendations_success(
    mock_ai_kernel,
    mock_repo,
    mock_context_engine,
    mock_trace_service,
    mock_event_bus,
    op_ctx,
    dummy_command,
):
    mock_enterprise_context = MagicMock()
    mock_enterprise_context.sections = []
    mock_context_engine.build.return_value = mock_enterprise_context

    mock_ai_kernel.classify.return_value = ClassifyResponse(
        raw_json={
            "recommendations": [
                {
                    "title": "Rec 1",
                    "body": "Do this",
                    "rationale": "Because",
                    "confidence": "high",
                    "supporting_memory_refs": [],
                    "supporting_goal_refs": [],
                }
            ]
        },
        metadata=AIResponseMetadata(provider="test", model="test", latency_ms=10.0),
    )

    mock_rec = MagicMock(spec=Recommendation)
    mock_rec.id = uuid4()
    mock_repo.create.return_value = mock_rec

    mock_trace_result = MagicMock()
    mock_trace_result.trace = None
    mock_trace_service.record_operation.return_value = mock_trace_result

    engine = RecommendationEngine(
        ai_kernel=mock_ai_kernel,
        repository=mock_repo,
        context_engine=mock_context_engine,
        trace_service=mock_trace_service,
        event_bus=mock_event_bus,
    )

    result = await engine.generate_recommendations(op_ctx, dummy_command)

    assert isinstance(result, GenerateRecommendationsResult)
    assert len(result.recommendations) == 1
    assert result.recommendations[0] == mock_rec
    assert result.dispatched_events == 1

    mock_context_engine.build.assert_called_once()
    mock_ai_kernel.classify.assert_called_once()
    mock_repo.create.assert_called_once()
    mock_trace_service.record_operation.assert_called_once()
    mock_event_bus.publish.assert_called_once()


@pytest.mark.asyncio
async def test_generate_recommendations_ai_error(
    mock_ai_kernel,
    mock_repo,
    mock_context_engine,
    mock_trace_service,
    mock_event_bus,
    op_ctx,
    dummy_command,
):
    mock_ai_kernel.classify.side_effect = ValueError("AI Failed")

    engine = RecommendationEngine(
        ai_kernel=mock_ai_kernel,
        repository=mock_repo,
        context_engine=mock_context_engine,
        trace_service=mock_trace_service,
        event_bus=mock_event_bus,
    )

    with pytest.raises(RecommendationGenerationError):
        await engine.generate_recommendations(op_ctx, dummy_command)


@pytest.mark.asyncio
async def test_generate_recommendations_validation_error(
    mock_ai_kernel,
    mock_repo,
    mock_context_engine,
    mock_trace_service,
    mock_event_bus,
    op_ctx,
    dummy_command,
):
    mock_ai_kernel.classify.return_value = ClassifyResponse(
        raw_json={"invalid": "payload"},
        metadata=AIResponseMetadata(provider="test", model="test", latency_ms=10.0),
    )

    engine = RecommendationEngine(
        ai_kernel=mock_ai_kernel,
        repository=mock_repo,
        context_engine=mock_context_engine,
        trace_service=mock_trace_service,
        event_bus=mock_event_bus,
    )

    with pytest.raises(AIOutputValidationError):
        await engine.generate_recommendations(op_ctx, dummy_command)


@pytest.mark.asyncio
async def test_generate_recommendations_no_valid_error(
    mock_ai_kernel,
    mock_repo,
    mock_context_engine,
    mock_trace_service,
    mock_event_bus,
    op_ctx,
    dummy_command,
):
    mock_ai_kernel.classify.return_value = ClassifyResponse(
        raw_json={"recommendations": []},
        metadata=AIResponseMetadata(provider="test", model="test", latency_ms=10.0),
    )

    engine = RecommendationEngine(
        ai_kernel=mock_ai_kernel,
        repository=mock_repo,
        context_engine=mock_context_engine,
        trace_service=mock_trace_service,
        event_bus=mock_event_bus,
    )

    with pytest.raises(RecommendationGenerationError):
        await engine.generate_recommendations(op_ctx, dummy_command)


@pytest.mark.asyncio
async def test_generate_recommendations_trace_failure(
    mock_ai_kernel,
    mock_repo,
    mock_context_engine,
    mock_trace_service,
    mock_event_bus,
    op_ctx,
    dummy_command,
):
    mock_enterprise_context = MagicMock()
    mock_enterprise_context.sections = []
    mock_context_engine.build.return_value = mock_enterprise_context

    mock_ai_kernel.classify.return_value = ClassifyResponse(
        raw_json={
            "recommendations": [
                {
                    "title": "Rec 1",
                    "body": "Do this",
                    "rationale": "Because",
                    "confidence": "high",
                }
            ]
        },
        metadata=AIResponseMetadata(provider="test", model="test", latency_ms=10.0),
    )

    mock_rec = MagicMock(spec=Recommendation)
    mock_rec.id = uuid4()
    mock_repo.create.return_value = mock_rec

    mock_trace_service.record_operation.side_effect = Exception("Trace failed")

    engine = RecommendationEngine(
        ai_kernel=mock_ai_kernel,
        repository=mock_repo,
        context_engine=mock_context_engine,
        trace_service=mock_trace_service,
        event_bus=mock_event_bus,
    )

    result = await engine.generate_recommendations(op_ctx, dummy_command)
    assert result.cognitive_trace is None
    assert len(result.recommendations) == 1
