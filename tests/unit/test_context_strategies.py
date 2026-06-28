import pytest
from datetime import datetime, timezone, timedelta
import uuid

from app.models.enterprise_context import (
    ContextItem,
    ContextSection,
    ContextProvenance,
)
from app.models.enums import ContextSource, ContextPriority
from app.services.context_policies import ContextPolicy
from app.services.context_strategies import (
    DefaultContextRanker,
    DefaultContextCompressor,
    DefaultContextWindowBuilder,
)

def create_mock_item(content: str, source: ContextSource, priority: ContextPriority, confidence: float = 1.0, token_estimate: int = 10, age_hours: int = 0, domain_object_id=None):
    prov = ContextProvenance(
        provider=source,
        service_name=f"{source.value}_provider",
        retrieval_timestamp=datetime.now(timezone.utc) - timedelta(hours=age_hours),
        confidence=confidence
    )
    return ContextItem(
        item_id=uuid.uuid4(),
        source=source,
        priority=priority,
        content=content,
        token_estimate=token_estimate,
        domain_object_id=domain_object_id,
        provenance=prov
    )

def test_ranker_ordering():
    ranker = DefaultContextRanker()
    policy = ContextPolicy(policy_id="test", name="Test", enabled_providers=[ContextSource.MEMORY, ContextSource.GOAL])
    
    item_old = create_mock_item("Old memory", ContextSource.MEMORY, ContextPriority.MEDIUM, age_hours=24)
    item_new = create_mock_item("New memory", ContextSource.MEMORY, ContextPriority.HIGH, age_hours=0)
    
    section = ContextSection(
        source=ContextSource.MEMORY,
        priority=ContextPriority.HIGH,
        items=[item_old, item_new],
        token_estimate=20
    )
    
    ranked_sections = ranker.rank([section], policy)
    assert len(ranked_sections) == 1
    
    ranked_items = ranked_sections[0].items
    assert len(ranked_items) == 2
    # New HIGH priority item should be ranked above Old MEDIUM priority item
    assert ranked_items[0].item_id == item_new.item_id
    assert ranked_items[1].item_id == item_old.item_id
    
    # Check that provenance ranking_score was updated
    assert ranked_items[0].provenance.ranking_score > ranked_items[1].provenance.ranking_score

def test_compressor_deduplication():
    compressor = DefaultContextCompressor()
    
    item1 = create_mock_item("Same content here", ContextSource.MEMORY, ContextPriority.HIGH)
    item2 = create_mock_item("  same content here  ", ContextSource.MEMORY, ContextPriority.MEDIUM)
    item3 = create_mock_item("Different content", ContextSource.MEMORY, ContextPriority.HIGH)
    
    # Manually assign ranking scores to simulate ranker output
    item1.provenance.ranking_score = 0.9
    item2.provenance.ranking_score = 0.5
    item3.provenance.ranking_score = 0.8
    
    section = ContextSection(
        source=ContextSource.MEMORY,
        priority=ContextPriority.HIGH,
        items=[item1, item2, item3],
        token_estimate=30
    )
    
    compressed_sections = compressor.compress([section], budget=1000)
    assert len(compressed_sections) == 1
    
    compressed_items = compressed_sections[0].items
    # item1 and item2 have same semantic fingerprint, item1 has higher rank
    # So we should be left with item1 and item3
    assert len(compressed_items) == 2
    
    contents = [i.content for i in compressed_items]
    assert "Same content here" in contents
    assert "Different content" in contents

def test_compressor_background_collapse():
    compressor = DefaultContextCompressor()
    
    bg_items = [create_mock_item(f"Bg {i}", ContextSource.MEMORY, ContextPriority.BACKGROUND) for i in range(5)]
    for bg in bg_items:
        bg.provenance.ranking_score = 0.1
    
    high_item = create_mock_item("High priority", ContextSource.MEMORY, ContextPriority.HIGH)
    high_item.provenance.ranking_score = 0.9
    
    section = ContextSection(
        source=ContextSource.MEMORY,
        priority=ContextPriority.HIGH,
        items=bg_items + [high_item],
        token_estimate=60
    )
    
    compressed_sections = compressor.compress([section], budget=1000)
    compressed_items = compressed_sections[0].items
    
    # 1 high priority + 1 collapsed background summary
    assert len(compressed_items) == 2
    
    summary_item = next(i for i in compressed_items if i.priority == ContextPriority.BACKGROUND)
    assert "Collapsed 5 background context items" in summary_item.content
    assert len(summary_item.provenance.compression_origin) == 5

def test_window_builder_packing():
    builder = DefaultContextWindowBuilder()
    
    critical_item = create_mock_item("Goal", ContextSource.GOAL, ContextPriority.CRITICAL, token_estimate=20)
    memory_item_1 = create_mock_item("Mem 1", ContextSource.MEMORY, ContextPriority.HIGH, token_estimate=50)
    memory_item_2 = create_mock_item("Mem 2", ContextSource.MEMORY, ContextPriority.MEDIUM, token_estimate=50)
    
    sections = [
        ContextSection(source=ContextSource.GOAL, priority=ContextPriority.CRITICAL, items=[critical_item], token_estimate=20),
        ContextSection(source=ContextSource.MEMORY, priority=ContextPriority.HIGH, items=[memory_item_1, memory_item_2], token_estimate=100)
    ]
    
    # Budget is 100 tokens. Reserve is 10 (10%).
    # Goal section uses 20. Remaining budget is 80. Reserve is safe? remaining_budget (80) - reserve (10) = 70.
    # We can fit Mem 1 (50) in 70 budget. Remaining budget = 20.
    # Mem 2 (50) cannot fit in 20. So it's excluded.
    window = builder.build_window(sections, budget=100)
    
    assert window.items_included == 2
    assert window.items_excluded == 1
    assert window.overflow is True
    
    packed_sources = [s.source for s in window.sections]
    assert ContextSource.GOAL in packed_sources
    assert ContextSource.MEMORY in packed_sources
    
    # Memory section should only have Mem 1
    memory_sec = next(s for s in window.sections if s.source == ContextSource.MEMORY)
    assert len(memory_sec.items) == 1
    assert memory_sec.items[0].content == "Mem 1"
    
    # Token estimate should be 20 + 50 = 70
    assert window.token_estimate == 70
