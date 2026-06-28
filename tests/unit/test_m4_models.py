import uuid
from datetime import datetime, timezone
import pytest
from pydantic import ValidationError

from app.models.enterprise_context import (
    ContextItem,
    ContextSection,
    ContextMetadata,
    ContextWindow,
    ContextSummary,
    ContextSchemaVersion,
    ContextProvenance,
    ProviderFailureRecord,
    EnterpriseContext,
)
from app.models.enums import ContextPriority, ContextSource, ContextStatus
from app.models.conversation import ConversationThread, ConversationTurn
from app.models.enums import ConversationRole, ConversationStatus

def test_context_item_validation():
    """Test ContextItem valid creation and immutability."""
    prov = ContextProvenance(
        provider=ContextSource.MEMORY,
        service_name="MemoryProvider"
    )
    
    item = ContextItem(
        item_id=uuid.uuid4(),
        source=ContextSource.MEMORY,
        content="This is a test memory",
        priority=ContextPriority.HIGH,
        token_estimate=5,
        provenance=prov
    )
    assert item.source == ContextSource.MEMORY
    
    with pytest.raises(ValidationError):
        ContextItem(
            source="INVALID_SOURCE", # type: ignore
            content="Bad",
            priority=ContextPriority.LOW,
            token_estimate=1,
            provenance=prov
        )

def test_context_section_validation():
    prov = ContextProvenance(
        provider=ContextSource.GOAL,
        service_name="GoalProvider"
    )
    item1 = ContextItem(
        source=ContextSource.GOAL, content="Goal 1",
        priority=ContextPriority.CRITICAL, token_estimate=10, provenance=prov
    )
    section = ContextSection(
        source=ContextSource.GOAL,
        priority=ContextPriority.CRITICAL,
        items=[item1],
        token_estimate=10
    )
    assert section.item_count == 1
    assert section.token_estimate == 10

def test_enterprise_context_lifecycle():
    """Test EnterpriseContext lifecycle states."""
    twin_id = uuid.uuid4()
    context_id = uuid.uuid4()
    
    metadata = ContextMetadata(
        policy_id="default",
        generated_at=datetime.now(timezone.utc),
        total_tokens=100
    )
    
    ctx = EnterpriseContext(
        context_id=context_id,
        twin_id=twin_id,
        schema_version=ContextSchemaVersion.V1,
        status=ContextStatus.BUILDING,
        sections=[],
        summary=None,
        metadata=metadata
    )
    
    assert ctx.status == ContextStatus.BUILDING
    assert ctx.context_id == context_id
    assert ctx.twin_id == twin_id

def test_conversation_thread_validation():
    twin_id = uuid.uuid4()
    thread_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    thread = ConversationThread(
        id=thread_id,
        twin_id=twin_id,
        title="Strategy Session",
        created_at=now,
        updated_at=now
    )
    
    assert thread.status == ConversationStatus.ACTIVE
    assert thread.twin_id == twin_id
    assert thread.title == "Strategy Session"

def test_conversation_turn_validation():
    thread_id = uuid.uuid4()
    turn_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    turn = ConversationTurn(
        id=turn_id,
        thread_id=thread_id,
        turn_index=0,
        role=ConversationRole.USER,
        content="What is my strategic goal?",
        created_at=now
    )
    
    assert turn.thread_id == thread_id
    assert turn.role == ConversationRole.USER
    assert turn.content == "What is my strategic goal?"

def test_provider_failure_record():
    failure = ProviderFailureRecord(
        provider=ContextSource.MEMORY,
        error_type="ConnectionError",
        error_message="Connection timeout",
        attempts=3
    )
    assert failure.provider == ContextSource.MEMORY
    assert failure.error_type == "ConnectionError"
    assert failure.error_message == "Connection timeout"
    assert failure.attempts == 3
