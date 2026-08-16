from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.application.recommendation.recommendation_engine import (
    AIOutputValidationError,
    RecommendationEngine,
    RecommendationGenerationError,
)
from app.core.context import OperationContext
from app.intelligence.decision.recommendation.recommendation import (
    Recommendation,
    RecommendationCreate,
)
from app.intelligence.learning.repository.cognitive_trace import CognitiveTrace
from app.runtime.core.commands import GenerateRecommendationsCommand


@pytest.fixture
def ctx():
    return OperationContext(correlation_id="test-corr-id")

@pytest.fixture
def command():
    return GenerateRecommendationsCommand(
        twin_id=uuid4(),
        context_window_id=uuid4()
    )

@pytest.fixture
def engine():
    ai_kernel = AsyncMock()
    repository = AsyncMock()
    context_engine = AsyncMock()
    trace_service = AsyncMock()
    event_bus = AsyncMock()

    engine = RecommendationEngine(
        ai_kernel=ai_kernel,
        repository=repository,
        context_engine=context_engine,
        trace_service=trace_service,
        event_bus=event_bus
    )

    # Mock enterprise context
    mock_context = MagicMock()
    mock_context.sections = []
    context_engine.build.return_value = mock_context

    # Mock AI response
    mock_response = MagicMock()
    mock_response.raw_json = [
        {
            "title": "Rec 1",
            "body": "Do this",
            "rationale": "Reason",
            "confidence": "high",
            "explainability_note": "A note"
        }
    ]
    mock_response.metadata.prompt_tokens = 10
    mock_response.metadata.completion_tokens = 20
    mock_response.metadata.provider = "test"
    mock_response.metadata.model = "test-model"
    ai_kernel.classify.return_value = mock_response

    # Mock persistence
    mock_rec = Recommendation.model_construct(
        id=uuid4(),
        twin_id=uuid4(),
        title="Rec 1",
        body="Do this",
        rationale="Reason",
        confidence="high",
        status="pending"
    )
    repository.create.return_value = mock_rec

    # Mock trace
    mock_trace = MagicMock()
    mock_trace.trace = CognitiveTrace.model_construct(
        id=uuid4(),
        twin_id=uuid4(),
        operation_type="recommendation_generation",
        provider="test",
        model="test-model",
        prompt_version="v1",
        operation_context_id="test-corr",
        reasoning_summary="test summary"
    )
    trace_service.record_operation.return_value = mock_trace

    return engine

@pytest.mark.asyncio
async def test_generate_recommendations_success(engine, ctx, command):
    result = await engine.generate_recommendations(ctx, command)

    assert len(result.recommendations) == 1
    assert result.cognitive_trace is not None

    engine._context_engine.build.assert_called_once()
    engine._ai_kernel.classify.assert_called_once()
    engine._repository.create.assert_called_once()
    engine._trace_service.record_operation.assert_called_once()
    engine._event_bus.publish.assert_called_once()

@pytest.mark.asyncio
async def test_generate_recommendations_ai_error(engine, ctx, command):
    engine._ai_kernel.classify.side_effect = ValueError("AI Error")

    with pytest.raises(RecommendationGenerationError):
        await engine.generate_recommendations(ctx, command)

@pytest.mark.asyncio
async def test_generate_recommendations_validation_error(engine, ctx, command):
    engine._ai_kernel.classify.return_value.raw_json = {"invalid": "data"}

    with pytest.raises(AIOutputValidationError):
        await engine.generate_recommendations(ctx, command)

@pytest.mark.asyncio
async def test_generate_recommendations_no_results(engine, ctx, command):
    engine._ai_kernel.classify.return_value.raw_json = []

    with pytest.raises(RecommendationGenerationError):
        await engine.generate_recommendations(ctx, command)
