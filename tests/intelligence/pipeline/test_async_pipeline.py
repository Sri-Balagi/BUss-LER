from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.intelligence.core.session.events import SessionEventType
from app.intelligence.core.session.models import SessionLifecycleState
from app.intelligence.core.session.session import CognitiveSession
from app.intelligence.pipeline.phases import IPhase, PhaseResult, PhaseResultStatus, PipelinePhase
from app.intelligence.pipeline.pipeline import AsyncCognitivePipeline


class MockPhase(IPhase):
    def __init__(self, phase_type, result_status=PhaseResultStatus.SUCCESS, error_message=None, should_raise=False):
        self._phase_type = phase_type
        self.result_status = result_status
        self.error_message = error_message
        self.should_raise = should_raise
        self.executed = False

    @property
    def phase_type(self) -> PipelinePhase:
        return self._phase_type

    async def execute(self, session):
        self.executed = True
        if self.should_raise:
            raise Exception("Mock Exception")
        return PhaseResult(phase=self.phase_type, status=self.result_status, error_message=self.error_message)

@pytest.fixture
def mock_session():
    session = MagicMock(spec=CognitiveSession)
    session.session_id = uuid4()
    session.is_runnable = True
    session.should_terminate.return_value = False
    session.execution_history = []

    def side_effect():
        if len(session.execution_history) > 0:
            return True
        return False
    session.should_terminate.side_effect = side_effect

    def record_cycle(record):
        session.execution_history.append(record)
    session.record_cycle.side_effect = record_cycle

    # Mock transition to update should_terminate or is_runnable if needed
    def transition(state, reason=None):
        session.lifecycle_state = state
        if state == SessionLifecycleState.AWAITING_INPUT:
            session.is_runnable = False
    session.transition.side_effect = transition

    return session

@pytest.mark.asyncio
async def test_pipeline_success(mock_session):
    phase1 = MockPhase(PipelinePhase.OBSERVE)
    phase2 = MockPhase(PipelinePhase.REASON)

    mock_bus = MagicMock()

    pipeline = AsyncCognitivePipeline([phase1, phase2], event_bus_factory=lambda x: mock_bus)

    await pipeline.run_loop(mock_session)

    assert phase1.executed
    assert phase2.executed
    assert mock_bus.publish.call_count == 2
    # Check that events were published
    args, kwargs = mock_bus.publish.call_args_list[0]
    assert args[0].event_type == SessionEventType.PHASE_COMPLETED

@pytest.mark.asyncio
async def test_pipeline_yielded(mock_session):
    phase1 = MockPhase(PipelinePhase.OBSERVE, PhaseResultStatus.YIELDED)
    phase2 = MockPhase(PipelinePhase.REASON)

    pipeline = AsyncCognitivePipeline([phase1, phase2])

    await pipeline.run_loop(mock_session)

    assert phase1.executed
    assert not phase2.executed
    mock_session.transition.assert_called_with(SessionLifecycleState.AWAITING_INPUT, reason="Yielded by OBSERVE")

@pytest.mark.asyncio
async def test_pipeline_failed_phase(mock_session):
    phase1 = MockPhase(PipelinePhase.OBSERVE, PhaseResultStatus.FAILED, "error")
    phase2 = MockPhase(PipelinePhase.REASON)

    pipeline = AsyncCognitivePipeline([phase1, phase2])
    await pipeline.run_loop(mock_session)

    assert phase1.executed
    assert not phase2.executed

@pytest.mark.asyncio
async def test_pipeline_exception_in_phase(mock_session):
    phase1 = MockPhase(PipelinePhase.OBSERVE, should_raise=True)
    phase2 = MockPhase(PipelinePhase.REASON)

    mock_bus = MagicMock()
    pipeline = AsyncCognitivePipeline([phase1, phase2], event_bus_factory=lambda x: mock_bus)

    await pipeline.run_loop(mock_session)

    assert phase1.executed
    assert not phase2.executed
    assert mock_bus.publish.call_count == 1
    args, kwargs = mock_bus.publish.call_args_list[0]
    assert args[0].event_type == SessionEventType.PHASE_FAILED
