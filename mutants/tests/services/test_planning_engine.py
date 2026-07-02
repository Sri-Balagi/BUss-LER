from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from app.models.ai import AIResponseMetadata, ClassifyResponse
from app.models.commands import GeneratePlanCommand
from app.models.exceptions import AIOutputValidationError, PlanGenerationError
from app.models.results import GeneratePlanResult
from app.services.planning_engine import PlanningEngine

from app.core.context import OperationContext


@pytest.fixture
def mock_ai_kernel():
    return AsyncMock()


@pytest.fixture
def mock_plan_repo():
    return AsyncMock()


@pytest.fixture
def mock_context_engine():
    return AsyncMock()


@pytest.fixture
def mock_goal_service():
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
    return GeneratePlanCommand(twin_id=uuid4(), goal_id=uuid4(), intent_id=uuid4())


@pytest.mark.asyncio
async def test_generate_plan_success(
    mock_ai_kernel,
    mock_plan_repo,
    mock_context_engine,
    mock_goal_service,
    mock_trace_service,
    mock_event_bus,
    op_ctx,
    dummy_command,
):
    mock_goal = MagicMock()
    mock_goal.title = "Test Goal"
    mock_goal.description = "Goal desc"
    mock_goal_service.get_goal.return_value = mock_goal

    mock_enterprise_context = MagicMock()
    mock_enterprise_context.sections = []
    mock_context_engine.build.return_value = mock_enterprise_context

    mock_ai_kernel.classify.return_value = ClassifyResponse(
        raw_json={
            "rationale": "Because testing is good",
            "steps": [
                {
                    "step_number": 1,
                    "action": "Write tests",
                    "expected_outcome": "Tests pass",
                }
            ],
            "confidence": 0.9,
        },
        metadata=AIResponseMetadata(provider="test", model="test", latency_ms=10.0),
    )

    from app.models.plan import Plan, PlanStep

    mock_plan = Plan(
        id=uuid4(),
        twin_id=dummy_command.twin_id,
        goal_id=dummy_command.goal_id,
        intent_id=dummy_command.intent_id,
        rationale="Because",
        steps=[PlanStep(step_number=1, action="Write tests", expected_outcome="Pass")],
        confidence=0.9,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    mock_plan_repo.create.return_value = mock_plan

    mock_trace_result = MagicMock()
    mock_trace_result.trace = None
    mock_trace_service.record_operation.return_value = mock_trace_result

    engine = PlanningEngine(
        ai_kernel=mock_ai_kernel,
        plan_repository=mock_plan_repo,
        context_engine=mock_context_engine,
        goal_service=mock_goal_service,
        trace_service=mock_trace_service,
        event_bus=mock_event_bus,
    )

    result = await engine.generate_plan(op_ctx, dummy_command)

    assert isinstance(result, GeneratePlanResult)
    assert result.plan == mock_plan
    assert result.dispatched_events == 1

    mock_goal_service.get_goal.assert_called_once_with(op_ctx, dummy_command.goal_id)
    mock_context_engine.build.assert_called_once()
    mock_ai_kernel.classify.assert_called_once()
    mock_plan_repo.create.assert_called_once()
    mock_trace_service.record_operation.assert_called_once()
    mock_event_bus.publish.assert_called_once()


@pytest.mark.asyncio
async def test_generate_plan_ai_error(
    mock_ai_kernel,
    mock_plan_repo,
    mock_context_engine,
    mock_goal_service,
    mock_trace_service,
    mock_event_bus,
    op_ctx,
    dummy_command,
):
    mock_ai_kernel.classify.side_effect = ValueError("AI Failed")

    engine = PlanningEngine(
        ai_kernel=mock_ai_kernel,
        plan_repository=mock_plan_repo,
        context_engine=mock_context_engine,
        goal_service=mock_goal_service,
        trace_service=mock_trace_service,
        event_bus=mock_event_bus,
    )

    with pytest.raises((PlanGenerationError, AIOutputValidationError)):
        await engine.generate_plan(op_ctx, dummy_command)


@pytest.mark.asyncio
async def test_generate_plan_validation_error(
    mock_ai_kernel,
    mock_plan_repo,
    mock_context_engine,
    mock_goal_service,
    mock_trace_service,
    mock_event_bus,
    op_ctx,
    dummy_command,
):
    mock_ai_kernel.classify.return_value = ClassifyResponse(
        raw_json={"invalid": "payload"},
        metadata=AIResponseMetadata(provider="test", model="test", latency_ms=10.0),
    )

    engine = PlanningEngine(
        ai_kernel=mock_ai_kernel,
        plan_repository=mock_plan_repo,
        context_engine=mock_context_engine,
        goal_service=mock_goal_service,
        trace_service=mock_trace_service,
        event_bus=mock_event_bus,
    )

    with pytest.raises(AIOutputValidationError):
        await engine.generate_plan(op_ctx, dummy_command)


@pytest.mark.asyncio
async def test_generate_plan_no_steps_error(
    mock_ai_kernel,
    mock_plan_repo,
    mock_context_engine,
    mock_goal_service,
    mock_trace_service,
    mock_event_bus,
    op_ctx,
    dummy_command,
):
    mock_ai_kernel.classify.return_value = ClassifyResponse(
        raw_json={
            "rationale": "Because testing is good",
            "steps": [],
            "confidence": 0.9,
        },
        metadata=AIResponseMetadata(provider="test", model="test", latency_ms=10.0),
    )

    engine = PlanningEngine(
        ai_kernel=mock_ai_kernel,
        plan_repository=mock_plan_repo,
        context_engine=mock_context_engine,
        goal_service=mock_goal_service,
        trace_service=mock_trace_service,
        event_bus=mock_event_bus,
    )

    with pytest.raises((PlanGenerationError, AIOutputValidationError)):
        await engine.generate_plan(op_ctx, dummy_command)


@pytest.mark.asyncio
async def test_generate_plan_trace_failure(
    mock_ai_kernel,
    mock_plan_repo,
    mock_context_engine,
    mock_goal_service,
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
            "rationale": "Because testing is good",
            "steps": [
                {
                    "step_number": 1,
                    "action": "Write tests",
                    "expected_outcome": "Tests pass",
                }
            ],
            "confidence": 0.9,
        },
        metadata=AIResponseMetadata(provider="test", model="test", latency_ms=10.0),
    )

    from app.models.plan import Plan, PlanStep

    mock_plan = Plan(
        id=uuid4(),
        twin_id=dummy_command.twin_id,
        goal_id=dummy_command.goal_id,
        intent_id=dummy_command.intent_id,
        rationale="Because",
        steps=[PlanStep(step_number=1, action="Write tests", expected_outcome="Pass")],
        confidence=0.9,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    mock_plan_repo.create.return_value = mock_plan

    mock_trace_service.record_operation.side_effect = Exception("Trace failed")

    engine = PlanningEngine(
        ai_kernel=mock_ai_kernel,
        plan_repository=mock_plan_repo,
        context_engine=mock_context_engine,
        goal_service=mock_goal_service,
        trace_service=mock_trace_service,
        event_bus=mock_event_bus,
    )

    result = await engine.generate_plan(op_ctx, dummy_command)
    assert result.cognitive_trace is None
