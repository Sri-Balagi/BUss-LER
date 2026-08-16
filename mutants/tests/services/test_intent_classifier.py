from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from app.models.ai import AIResponseMetadata, ClassifyResponse
from app.models.exceptions import AIOutputValidationError, IntentClassificationError
from app.models.intent import Intent
from app.models.results import ClassifyIntentResult
from app.services.intent_classifier import IntentClassifier

from app.core.context import OperationContext


@pytest.fixture
def mock_ai_kernel():
    return AsyncMock()


@pytest.fixture
def mock_trace_service():
    return AsyncMock()


@pytest.fixture
def op_ctx():
    return OperationContext(correlation_id="test-corr-id")


@pytest.fixture
def dummy_intent():
    return Intent(
        id=uuid4(),
        twin_id=uuid4(),
        raw_text="Plan my next meeting",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.mark.asyncio
async def test_classify_success(mock_ai_kernel, mock_trace_service, op_ctx, dummy_intent):
    mock_ai_kernel.classify.return_value = ClassifyResponse(
        raw_json={
            "intent_type": "general",
            "confidence": "high",
            "business_domain": "operations",
            "reasoning_metadata": {"key_signals": ["meeting"]},
        },
        metadata=AIResponseMetadata(
            provider="test",
            model="test-model",
            latency_ms=10.0,
            prompt_tokens=10,
            completion_tokens=20,
        ),
    )

    mock_trace_result = MagicMock()
    mock_trace_result.trace = None
    mock_trace_service.record_operation.return_value = mock_trace_result

    classifier = IntentClassifier(ai_kernel=mock_ai_kernel, trace_service=mock_trace_service)
    result = await classifier.classify(op_ctx, dummy_intent)

    assert isinstance(result, ClassifyIntentResult)
    assert result.intent == dummy_intent
    assert result.analysis.intent_type.value == "general"
    assert result.analysis.confidence.value == "high"
    assert result.cognitive_trace == mock_trace_result.trace

    mock_ai_kernel.classify.assert_called_once()
    mock_trace_service.record_operation.assert_called_once()


@pytest.mark.asyncio
async def test_classify_ai_kernel_returns_non_json(
    mock_ai_kernel, mock_trace_service, op_ctx, dummy_intent
):
    mock_ai_kernel.classify.side_effect = ValueError("Not JSON")

    classifier = IntentClassifier(ai_kernel=mock_ai_kernel, trace_service=mock_trace_service)

    with pytest.raises(IntentClassificationError):
        await classifier.classify(op_ctx, dummy_intent)


@pytest.mark.asyncio
async def test_classify_ai_kernel_unexpected_error(
    mock_ai_kernel, mock_trace_service, op_ctx, dummy_intent
):
    mock_ai_kernel.classify.side_effect = Exception("Unknown failure")

    classifier = IntentClassifier(ai_kernel=mock_ai_kernel, trace_service=mock_trace_service)

    with pytest.raises(IntentClassificationError):
        await classifier.classify(op_ctx, dummy_intent)


@pytest.mark.asyncio
async def test_classify_pydantic_validation_error(
    mock_ai_kernel, mock_trace_service, op_ctx, dummy_intent
):
    mock_ai_kernel.classify.return_value = ClassifyResponse(
        raw_json={
            "intent_type": "invalid_enum_value",
            "confidence": "high",
            "reasoning_metadata": {},
        },
        metadata=AIResponseMetadata(
            provider="test",
            model="test",
            latency_ms=10.0,
            prompt_tokens=10,
            completion_tokens=10,
        ),
    )

    classifier = IntentClassifier(ai_kernel=mock_ai_kernel, trace_service=mock_trace_service)

    with pytest.raises(AIOutputValidationError):
        await classifier.classify(op_ctx, dummy_intent)


@pytest.mark.asyncio
async def test_classify_trace_service_fails_passively(
    mock_ai_kernel, mock_trace_service, op_ctx, dummy_intent
):
    mock_ai_kernel.classify.return_value = ClassifyResponse(
        raw_json={
            "intent_type": "general",
            "confidence": "high",
            "business_domain": "operations",
            "reasoning_metadata": {},
        },
        metadata=AIResponseMetadata(provider="test", model="test", latency_ms=10.0),
    )

    mock_trace_service.record_operation.side_effect = Exception("Trace DB offline")

    classifier = IntentClassifier(ai_kernel=mock_ai_kernel, trace_service=mock_trace_service)
    result = await classifier.classify(op_ctx, dummy_intent)

    assert isinstance(result, ClassifyIntentResult)
    assert result.analysis.intent_type.value == "general"
    assert result.cognitive_trace is None
