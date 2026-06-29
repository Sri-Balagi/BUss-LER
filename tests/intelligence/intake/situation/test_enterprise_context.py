import uuid
from datetime import datetime, timezone
import pytest
from pydantic import ValidationError

from app.intelligence.intake.situation.enterprise_context import (
    ContextItem,
    ContextSection,
    ContextMetadata,
    ContextSchemaVersion,
    ContextProvenance,
    ProviderFailureRecord,
    EnterpriseContext,
)
from app.shared.enums import ContextPriority, ContextSource, ContextStatus


def test_context_item_validation():
    """Test ContextItem valid creation and immutability."""
    prov = ContextProvenance(
        provider=ContextSource.MEMORY, service_name="MemoryProvider"
    )

    item = ContextItem(
        item_id=uuid.uuid4(),
        source=ContextSource.MEMORY,
        content="This is a test memory",
        priority=ContextPriority.HIGH,
        token_estimate=5,
        provenance=prov,
    )
    assert item.source == ContextSource.MEMORY

    with pytest.raises(ValidationError):
        ContextItem(
            source="INVALID_SOURCE",  # type: ignore
            content="Bad",
            priority=ContextPriority.LOW,
            token_estimate=1,
            provenance=prov,
        )


def test_context_section_validation():
    prov = ContextProvenance(provider=ContextSource.GOAL, service_name="GoalProvider")
    item1 = ContextItem(
        source=ContextSource.GOAL,
        content="Goal 1",
        priority=ContextPriority.CRITICAL,
        token_estimate=10,
        provenance=prov,
    )
    section = ContextSection(
        source=ContextSource.GOAL,
        priority=ContextPriority.CRITICAL,
        items=[item1],
        token_estimate=10,
    )
    assert section.item_count == 1
    assert section.token_estimate == 10


def test_enterprise_context_lifecycle():
    """Test EnterpriseContext lifecycle states."""
    twin_id = uuid.uuid4()
    context_id = uuid.uuid4()

    metadata = ContextMetadata(
        policy_id="default", generated_at=datetime.now(timezone.utc), total_tokens=100
    )

    ctx = EnterpriseContext(
        context_id=context_id,
        twin_id=twin_id,
        schema_version=ContextSchemaVersion.V1,
        status=ContextStatus.BUILDING,
        sections=[],
        summary=None,
        metadata=metadata,
    )

    assert ctx.status == ContextStatus.BUILDING
    assert ctx.context_id == context_id
    assert ctx.twin_id == twin_id


def test_provider_failure_record():
    failure = ProviderFailureRecord(
        provider=ContextSource.MEMORY,
        error_type="ConnectionError",
        error_message="Connection timeout",
        attempts=3,
    )
    assert failure.provider == ContextSource.MEMORY
    assert failure.error_type == "ConnectionError"
    assert failure.error_message == "Connection timeout"
    assert failure.attempts == 3
