import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.models.enterprise_context import ContextItem, ContextProvenance, ContextSection
from app.models.enums import ContextPriority, ContextSource
from app.services.context_policies import BUILT_IN_POLICIES
from app.services.context_strategies import (
    DefaultContextRanker,
    DefaultContextCompressor,
    DefaultContextWindowBuilder,
)


@pytest.fixture
def ranker():
    return DefaultContextRanker()


@pytest.fixture
def compressor():
    return DefaultContextCompressor()


@pytest.fixture
def window_builder():
    return DefaultContextWindowBuilder()


@pytest.fixture
def policy():
    return BUILT_IN_POLICIES["planning"]


def create_item(
    content: str,
    priority: ContextPriority = ContextPriority.MEDIUM,
    source: ContextSource = ContextSource.MEMORY,
    confidence: float = 0.5,
    age_hours: float = 0.0,
    has_domain_id: bool = False,
    domain_object_id=None,
) -> ContextItem:
    item_id = uuid4()
    domain_id = (
        domain_object_id if domain_object_id else (uuid4() if has_domain_id else None)
    )
    prov = ContextProvenance(
        provider=source,
        service_name="test",
        retrieval_timestamp=datetime.now(timezone.utc) - timedelta(hours=age_hours),
        confidence=confidence,
    )
    return ContextItem(
        item_id=item_id,
        source=source,
        priority=priority,
        content=content,
        domain_object_id=domain_id,
        token_estimate=len(content) // 4,
        provenance=prov,
    )


def test_ranker_ordering(ranker, policy):
    # Test scoring weights
    item1 = create_item("Low conf old", confidence=0.2, age_hours=10)
    item2 = create_item("High conf new", confidence=0.9, age_hours=0)
    item3 = create_item("High priority", priority=ContextPriority.CRITICAL)
    item4 = create_item("Has domain object", has_domain_id=True)

    section = ContextSection(
        section_id=uuid4(),
        source=ContextSource.MEMORY,
        priority=ContextPriority.MEDIUM,
        items=[item1, item2, item3, item4],
        token_estimate=100,
        retrieved_at=datetime.now(timezone.utc),
    )

    ranked_sections = ranker.rank([section], policy)
    assert len(ranked_sections) == 1
    ranked_items = ranked_sections[0].items
    assert len(ranked_items) == 4

    # Items should be ordered by score descending
    scores = [i.provenance.ranking_score for i in ranked_items]
    assert sorted(scores, reverse=True) == scores


def test_ranker_section_ordering(ranker, policy):
    # Intent should be first, then Goal, then others
    section_mem = ContextSection(
        section_id=uuid4(),
        source=ContextSource.MEMORY,
        priority=ContextPriority.MEDIUM,
        items=[],
        token_estimate=0,
        retrieved_at=datetime.now(timezone.utc),
    )
    section_intent = ContextSection(
        section_id=uuid4(),
        source=ContextSource.INTENT,
        priority=ContextPriority.MEDIUM,
        items=[],
        token_estimate=0,
        retrieved_at=datetime.now(timezone.utc),
    )

    ranked_sections = ranker.rank([section_mem, section_intent], policy)
    assert ranked_sections[0].source == ContextSource.INTENT
    assert ranked_sections[1].source == ContextSource.MEMORY


def test_ranker_invalid_source_ordering(ranker, policy):
    # Edge case: ContextSource not in ordering list
    # Not easy to produce a totally fake source type without breaking enum,
    # but we can just use a source that might be added later or one that is at the end.
    assert ranker._section_order("UNKNOWN_SOURCE") == 10  # len(_SECTION_PRIORITY_ORDER)


def test_compressor_deduplication(compressor):
    # Create two items with same content, provider, and domain id
    domain_id = uuid4()
    item1 = create_item(
        "same content", source=ContextSource.MEMORY, domain_object_id=domain_id
    )
    item1.provenance.ranking_score = 0.5
    item2 = create_item(
        "  SAME content  ", source=ContextSource.MEMORY, domain_object_id=domain_id
    )
    item2.provenance.ranking_score = 0.9  # Should be kept

    section = ContextSection(
        section_id=uuid4(),
        source=ContextSource.MEMORY,
        priority=ContextPriority.MEDIUM,
        items=[item1, item2],
        token_estimate=100,
        retrieved_at=datetime.now(timezone.utc),
    )

    compressed = compressor.compress([section], budget=1000)
    assert len(compressed) == 1
    assert len(compressed[0].items) == 1
    assert compressed[0].items[0].item_id == item2.item_id
    assert item1.item_id in compressed[0].items[0].provenance.compression_origin
    assert "Deduplicated" in compressed[0].items[0].provenance.compression_reason


def test_compressor_collapse_background(compressor):
    # 4 background items
    items = [
        create_item(f"bg {i}", priority=ContextPriority.BACKGROUND) for i in range(4)
    ]
    for i, it in enumerate(items):
        it.provenance.ranking_score = 0.1 * i

    section = ContextSection(
        section_id=uuid4(),
        source=ContextSource.MEMORY,
        priority=ContextPriority.MEDIUM,
        items=items,
        token_estimate=100,
        retrieved_at=datetime.now(timezone.utc),
    )

    compressed = compressor.compress([section], budget=1000)
    assert len(compressed) == 1
    assert len(compressed[0].items) == 1  # 4 background items collapsed into 1
    assert compressed[0].items[0].priority == ContextPriority.BACKGROUND
    assert "Collapsed 4 background" in compressed[0].items[0].content


def test_compressor_no_collapse_few_background(compressor):
    # 3 background items shouldn't collapse
    items = [
        create_item(f"bg {i}", priority=ContextPriority.BACKGROUND) for i in range(3)
    ]

    section = ContextSection(
        section_id=uuid4(),
        source=ContextSource.MEMORY,
        priority=ContextPriority.MEDIUM,
        items=items,
        token_estimate=100,
        retrieved_at=datetime.now(timezone.utc),
    )

    compressed = compressor.compress([section], budget=1000)
    assert len(compressed[0].items) == 3


def test_window_builder(window_builder):
    # Test greedy packing
    item1 = create_item("small item")  # 2 tokens
    item1.token_estimate = 2
    item2 = create_item("large item")  # 8 tokens
    item2.token_estimate = 8

    section = ContextSection(
        section_id=uuid4(),
        source=ContextSource.MEMORY,
        priority=ContextPriority.MEDIUM,
        items=[item1, item2],
        token_estimate=10,
        retrieved_at=datetime.now(timezone.utc),
    )

    # Budget 5: Only item1 fits
    window = window_builder.build_window([section], budget=5)
    assert window.items_included == 1
    assert window.items_excluded == 1
    assert window.overflow is True
    assert len(window.sections) == 1
    assert window.sections[0].items[0] == item1


def test_window_builder_critical_first(window_builder):
    # Goal section should be prioritized
    item1 = create_item("goal item", source=ContextSource.GOAL)
    item1.token_estimate = 10

    item2 = create_item("memory item", source=ContextSource.MEMORY)
    item2.token_estimate = 10

    goal_section = ContextSection(
        section_id=uuid4(),
        source=ContextSource.GOAL,
        priority=ContextPriority.CRITICAL,
        items=[item1],
        token_estimate=10,
        retrieved_at=datetime.now(timezone.utc),
    )
    mem_section = ContextSection(
        section_id=uuid4(),
        source=ContextSource.MEMORY,
        priority=ContextPriority.MEDIUM,
        items=[item2],
        token_estimate=10,
        retrieved_at=datetime.now(timezone.utc),
    )

    # Budget 15: both can't fit. Goal is packed first.
    window = window_builder.build_window([goal_section, mem_section], budget=15)
    assert window.items_included == 1
    assert window.sections[0].source == ContextSource.GOAL


def test_window_builder_section_empty(window_builder):
    # Section with items that don't fit
    item = create_item("huge", source=ContextSource.MEMORY)
    item.token_estimate = 100
    section = ContextSection(
        section_id=uuid4(),
        source=ContextSource.MEMORY,
        priority=ContextPriority.MEDIUM,
        items=[item],
        token_estimate=100,
        retrieved_at=datetime.now(timezone.utc),
    )
    window = window_builder.build_window([section], budget=50)
    assert window.items_included == 0
    assert len(window.sections) == 0
    assert window.overflow is True


def test_window_builder_zero_budget_skip(window_builder):
    # Tests the 'if remaining_budget <= 0: continue' block
    item1 = create_item("goal", source=ContextSource.GOAL)
    item1.token_estimate = 10
    goal_section = ContextSection(
        section_id=uuid4(),
        source=ContextSource.GOAL,
        priority=ContextPriority.CRITICAL,
        items=[item1],
        token_estimate=10,
        retrieved_at=datetime.now(timezone.utc),
    )

    item2 = create_item("mem1", source=ContextSource.MEMORY)
    item2.token_estimate = 5
    mem_section1 = ContextSection(
        section_id=uuid4(),
        source=ContextSource.MEMORY,
        priority=ContextPriority.MEDIUM,
        items=[item2],
        token_estimate=5,
        retrieved_at=datetime.now(timezone.utc),
    )

    # Budget 10, goal takes 10, remaining_budget = 0
    window = window_builder.build_window([goal_section, mem_section1], budget=10)
    assert window.items_included == 1
    assert window.items_excluded == 1
    assert window.overflow is True
