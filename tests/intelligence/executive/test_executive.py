import asyncio
import uuid
from typing import Any

import pytest

from app.intelligence.core.session.events import SessionEvent, SessionEventType
from app.intelligence.core.session.models import (
    ReasoningMode,
    SessionLifecycleState,
)
from app.intelligence.core.session.session import (
    CognitiveSession,
    InvalidSessionTransitionError,
)
from app.intelligence.executive.controller import ExecutiveController
from app.intelligence.executive.session_factory import SessionFactory
from app.intelligence.integration.interfaces import ICognitivePipeline
from app.intelligence.integration.models import (
    CognitivePipelineState,
    ExecutiveIntelligenceResult,
    IntegrationSummary,
    PipelineMetrics,
)


class MockPipeline(ICognitivePipeline):
    def run_pipeline(
        self, raw_request: str, session: CognitiveSession
    ) -> ExecutiveIntelligenceResult:
        if raw_request == "fail":
            raise ValueError("Pipeline forced failure")
            
        summary = IntegrationSummary(
            state=CognitivePipelineState.COMPLETED,
            metrics=PipelineMetrics(),
            warnings=[]
        )
        return ExecutiveIntelligenceResult(
            session_id=session.session_id,
            summary=summary
        )


class MockSessionFactory(SessionFactory):
    def __init__(self):
        super().__init__(None)


@pytest.fixture
def mock_pipeline():
    return MockPipeline()


@pytest.fixture
def session_factory():
    return MockSessionFactory()


@pytest.fixture
def controller(mock_pipeline, session_factory):
    return ExecutiveController(pipeline=mock_pipeline, session_factory=session_factory)


def test_cognitive_session_transitions():
    session = CognitiveSession()
    assert session.lifecycle_state == SessionLifecycleState.CREATED
    
    session.transition(SessionLifecycleState.RUNNING)
    assert session.lifecycle_state == SessionLifecycleState.RUNNING
    
    session.transition(SessionLifecycleState.SUSPENDED)
    assert session.lifecycle_state == SessionLifecycleState.SUSPENDED
    
    session.transition(SessionLifecycleState.RUNNING)
    
    session.transition(SessionLifecycleState.COMPLETED)
    assert session.lifecycle_state == SessionLifecycleState.COMPLETED
    
    with pytest.raises(InvalidSessionTransitionError):
        session.transition(SessionLifecycleState.RUNNING)


@pytest.mark.asyncio
async def test_executive_controller_success(controller):
    twin_id = uuid.uuid4()
    result = await controller.process_request("Optimize the business", twin_id=twin_id)
    
    assert isinstance(result, ExecutiveIntelligenceResult)
    assert result.summary.state == CognitivePipelineState.COMPLETED
    
    # In M7, the session is created, executes, and completes synchronously inside process_request.
    # The active_sessions dict should be empty because it cleans up in the finally block.
    assert len(controller._active_sessions) == 0


@pytest.mark.asyncio
async def test_executive_controller_failure(controller):
    with pytest.raises(ValueError, match="Pipeline forced failure"):
        await controller.process_request("fail")
