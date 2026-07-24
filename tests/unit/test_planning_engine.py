from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.application.planning.planning_engine import (
    AIOutputValidationError,
    PlanGenerationError,
    PlanningEngine,
)
from app.core.context import OperationContext
from app.intelligence.decision.planning.plan import Plan, PlanCreate, PlanStep
from app.intelligence.learning.repository.cognitive_trace import CognitiveTrace
from app.runtime.core.commands import GeneratePlanCommand


@pytest.fixture
def ctx():
    return OperationContext(correlation_id="test-corr-id")

@pytest.fixture
def command():
    return GeneratePlanCommand(
        twin_id=uuid4(),
        goal_id=uuid4(),
        intent_id=uuid4()
    )

@pytest.fixture
def engine():
    ai_kernel = AsyncMock()
    plan_repository = AsyncMock()
    context_engine = AsyncMock()
    goal_service = AsyncMock()
    trace_service = AsyncMock()
    event_bus = AsyncMock()

    engine = PlanningEngine(
        ai_kernel=ai_kernel,
        plan_repository=plan_repository,
        context_engine=context_engine,
        goal_service=goal_service,
        trace_service=trace_service,
        event_bus=event_bus
    )

    # Mock goal
    mock_goal = MagicMock()
    mock_goal.title = "Test Goal"
    mock_goal.description = "Test Desc"
    goal_service.get_goal.return_value = mock_goal

    # Mock enterprise context
    mock_context = MagicMock()
    mock_context.sections = []
    context_engine.build.return_value = mock_context

    # Mock AI response
    mock_response = MagicMock()
    mock_response.raw_json = {
        "title": "Test Plan",
        "rationale": "Reasoning",
        "confidence": 0.9,
        "steps": [
            {
                "title": "Step 1",
                "description": "Do this",
                "estimated_duration_hours": 1.0,
                "dependencies": []
            }
        ]
    }
    mock_response.metadata.prompt_tokens = 10
    mock_response.metadata.completion_tokens = 20
    mock_response.metadata.provider = "test"
    mock_response.metadata.model = "test-model"
    ai_kernel.classify.return_value = mock_response

    # Mock persistence
    mock_plan = Plan.model_construct(
        id=uuid4(),
        twin_id=uuid4(),
        goal_id=uuid4(),
        intent_id=uuid4(),
        title="Test Plan",
        rationale="Reasoning",
        confidence=0.9,
        steps=[PlanStep.model_construct(step_number=1, action="test", expected_outcome="test", title="Step 1")],
    )
    plan_repository.create.return_value = mock_plan

    # Mock trace
    mock_trace = MagicMock()
    mock_trace.trace = CognitiveTrace.model_construct(
        id=uuid4(),
        twin_id=uuid4(),
        operation_type="plan_generation",
        provider="test",
        model="test-model",
        prompt_version="v1",
        operation_context_id="test-corr",
        reasoning_summary="test summary"
    )
    trace_service.record_operation.return_value = mock_trace

    return engine

@pytest.mark.asyncio
async def test_generate_plan_success(engine, ctx, command):
    engine._ai_kernel.classify.return_value.raw_json = {
        "title": "Test Plan",
        "rationale": "Reasoning",
        "confidence": 0.9,
        "steps": [
            {
                "step_number": 1,
                "action": "Do this",
                "expected_outcome": "Success",
                "title": "Step 1",
                "description": "Details",
                "estimated_duration_hours": 1.0,
                "dependencies": []
            }
        ]
    }
    result = await engine.generate_plan(ctx, command)

    assert result.plan is not None
    assert result.cognitive_trace is not None

    engine._goal_service.get_goal.assert_called_once()
    engine._context_engine.build.assert_called_once()
    engine._ai_kernel.classify.assert_called_once()
    engine._plan_repository.create.assert_called_once()
    engine._trace_service.record_operation.assert_called_once()
    engine._event_bus.publish.assert_called_once()

@pytest.mark.asyncio
async def test_generate_plan_ai_error(engine, ctx, command):
    engine._ai_kernel.classify.side_effect = ValueError("AI Error")

    with pytest.raises(PlanGenerationError):
        await engine.generate_plan(ctx, command)

@pytest.mark.asyncio
async def test_generate_plan_validation_error(engine, ctx, command):
    engine._ai_kernel.classify.return_value.raw_json = {"invalid": "data"}

    with pytest.raises(AIOutputValidationError):
        await engine.generate_plan(ctx, command)

@pytest.mark.asyncio
async def test_generate_plan_no_steps(engine, ctx, command):
    engine._ai_kernel.classify.return_value.raw_json = {
        "title": "Test Plan",
        "rationale": "Reasoning",
        "confidence": 0.9,
        "steps": []
    }

    with pytest.raises(AIOutputValidationError):
        await engine.generate_plan(ctx, command)
