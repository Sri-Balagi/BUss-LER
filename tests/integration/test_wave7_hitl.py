import asyncio
import uuid

import pytest
from pydantic import ValidationError

from app.domain.approval.models import Approval, ApprovalState
from app.domain.session.models import Session, SessionStatus
from app.domain.shared.context import ExecutionContext
from app.infrastructure.notifications.sse_adapter import SSEAdapter
from app.shared.events.models import ApprovalRequestedEvent


def test_execution_context_immutability():
    ctx = ExecutionContext(
        tenant_id="t1",
        user_id="u1",
        session_id="s1",
        conversation_id="c1",
        trace_id="trace1",
        correlation_id="corr1"
    )
    # Attempting to mutate should raise ValidationError because Config.frozen=True
    with pytest.raises(ValidationError):
        ctx.user_id = "u2"

def test_approval_lifecycle():
    approval = Approval(
        target_type="JOB",
        target_id="job123",
        requested_by="system",
        state=ApprovalState.REQUIRED
    )
    assert approval.state == ApprovalState.REQUIRED

    approval.approve(user_id="manager1")
    assert approval.state == ApprovalState.APPROVED
    assert approval.approved_by == "manager1"
    assert approval.resolved_at is not None

def test_approval_rejection():
    approval = Approval(
        target_type="AGENT",
        target_id="agent456",
        requested_by="system",
        state=ApprovalState.REQUIRED
    )

    approval.reject(user_id="admin1", reason="Policy violation")
    assert approval.state == ApprovalState.REJECTED
    assert approval.reason == "Policy violation"
    assert approval.approved_by == "admin1"

def test_session_lifecycle():
    session = Session(tenant_id="t1", user_id="u1")
    assert session.status == SessionStatus.ACTIVE

    session.add_conversation("conv1")
    session.add_conversation("conv2")

    assert "conv1" in session.conversation_ids
    assert "conv2" in session.conversation_ids

    session.close()
    assert session.status == SessionStatus.CLOSED

@pytest.mark.asyncio
async def test_sse_adapter_dispatch():
    adapter = SSEAdapter()
    queue = adapter.subscribe()

    event = ApprovalRequestedEvent(
        correlation_id="corr1",
        approval_id="app1",
        tenant_id="t1",
        target_type="JOB",
        target_id="job1",
        requested_by="sys"
    )

    await adapter.dispatch(event)

    # Verify the event reaches the queue
    event_dict = await asyncio.wait_for(queue.get(), timeout=1.0)
    assert event_dict["event_id"] == str(event.event_id)
    assert event_dict["approval_id"] == "app1"

    adapter.unsubscribe(queue)
