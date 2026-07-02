from datetime import UTC, datetime
from uuid import UUID

import pytest
from app.models.enterprise_context import ContextItem, ContextProvenance, ContextSection
from app.models.enums import ContextPriority, ContextSource


@pytest.fixture
def stable_uuid1():
    return UUID("12345678-1234-5678-1234-567812345678")


@pytest.fixture
def stable_uuid2():
    return UUID("87654321-4321-8765-4321-876543210987")


def test_context_section_snapshot(snapshot, stable_uuid1, stable_uuid2):
    # Use a fixed datetime for the snapshot
    fixed_time = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)

    # Create a stable, deterministic section
    prov = ContextProvenance(
        provider=ContextSource.MEMORY,
        service_name="test_service",
        source=ContextSource.MEMORY,
        confidence=0.95,
        ranking_score=0.85,
        citations=["doc_123"],
        retrieval_timestamp=fixed_time,
    )

    item = ContextItem(
        item_id=str(stable_uuid1),
        source=ContextSource.MEMORY,
        priority=ContextPriority.MEDIUM,
        content="Stable business knowledge snapshot test.",
        content_type="memory",
        token_estimate=12,
        provenance=prov,
        domain_object_id=stable_uuid2,
    )

    section = ContextSection(
        section_id=str(stable_uuid1),
        source=ContextSource.MEMORY,
        items=[item],
        token_estimate=12,
        retrieved_at=fixed_time,
    )

    # Serialize to dict for snapshotting
    section_dict = section.model_dump(mode="json")

    assert section_dict == snapshot
