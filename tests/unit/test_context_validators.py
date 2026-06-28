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
from app.services.context_validators import DefaultContextValidator

def create_mock_item(item_id=None, source=ContextSource.MEMORY, conf=1.0, rank=1.0, future_date=False, citations=None, empty_prov=False):
    prov = None
    if not empty_prov:
        prov = ContextProvenance(
            provider=source,
            service_name="test",
            retrieval_timestamp=datetime.now(timezone.utc),
            confidence=conf,
            ranking_score=rank,
            citations=citations or []
        )
    if empty_prov:
        return ContextItem.model_construct(
            item_id=item_id or uuid.uuid4(),
            source=source,
            priority=ContextPriority.HIGH,
            content="Test content",
            token_estimate=10,
            provenance=None
        )
    else:
        return ContextItem(
            item_id=item_id or uuid.uuid4(),
            source=source,
            priority=ContextPriority.HIGH,
            content="Test content",
            token_estimate=10,
            provenance=prov
        )

def test_validator_success():
    validator = DefaultContextValidator()
    policy = ContextPolicy(
        policy_id="test",
        name="Test",
        enabled_providers=[ContextSource.MEMORY],
        required_providers=[ContextSource.MEMORY],
        token_budget=100
    )
    
    item = create_mock_item()
    section = ContextSection(
        source=ContextSource.MEMORY,
        priority=ContextPriority.HIGH,
        items=[item],
        token_estimate=10
    )
    
    result = validator.validate([section], policy)
    assert result.is_valid is True
    assert len(result.errors) == 0
    assert len(result.warnings) == 0

def test_validator_missing_required_provider():
    validator = DefaultContextValidator()
    policy = ContextPolicy(
        policy_id="test",
        name="Test",
        enabled_providers=[ContextSource.MEMORY, ContextSource.GOAL],
        required_providers=[ContextSource.GOAL],
        token_budget=100
    )
    
    item = create_mock_item(source=ContextSource.MEMORY)
    section = ContextSection(source=ContextSource.MEMORY, priority=ContextPriority.HIGH, items=[item])
    
    result = validator.validate([section], policy)
    assert result.is_valid is False
    assert any("GOAL" in e for e in result.errors)
    assert any("no active goals were found" in e for e in result.errors)

def test_validator_duplicate_items():
    validator = DefaultContextValidator()
    policy = ContextPolicy(policy_id="test", name="Test", enabled_providers=[ContextSource.MEMORY])
    
    item_id = uuid.uuid4()
    item1 = create_mock_item(item_id=item_id)
    item2 = create_mock_item(item_id=item_id)
    
    section = ContextSection(source=ContextSource.MEMORY, priority=ContextPriority.HIGH, items=[item1, item2])
    
    result = validator.validate([section], policy)
    # Warnings do not invalidate the context
    assert result.is_valid is True
    assert len(result.warnings) == 1
    assert "Duplicate ContextItem ID" in result.warnings[0]

def test_validator_missing_provenance():
    validator = DefaultContextValidator()
    policy = ContextPolicy(policy_id="test", name="Test", enabled_providers=[ContextSource.MEMORY])
    
    item = create_mock_item(empty_prov=True)
    section = ContextSection(source=ContextSource.MEMORY, priority=ContextPriority.HIGH, items=[item])
    
    result = validator.validate([section], policy)
    assert result.is_valid is False
    assert any("missing ContextProvenance" in e for e in result.errors)

def test_validator_future_timestamp():
    validator = DefaultContextValidator()
    policy = ContextPolicy(policy_id="test", name="Test", enabled_providers=[ContextSource.MEMORY])
    
    item = create_mock_item()
    section = ContextSection(
        source=ContextSource.MEMORY,
        priority=ContextPriority.HIGH,
        items=[item],
        retrieved_at=datetime.now(timezone.utc) + timedelta(hours=1)
    )
    
    result = validator.validate([section], policy)
    assert result.is_valid is False
    assert any("future retrieved_at timestamp" in e for e in result.errors)

def test_validator_confidence_bounds():
    validator = DefaultContextValidator()
    policy = ContextPolicy(policy_id="test", name="Test", enabled_providers=[ContextSource.MEMORY])
    
    prov = ContextProvenance.model_construct(
        provider=ContextSource.MEMORY,
        service_name="test",
        retrieval_timestamp=datetime.now(timezone.utc),
        confidence=1.5,
        ranking_score=-0.5,
        citations=[]
    )
    item = ContextItem.model_construct(
        item_id=uuid.uuid4(),
        source=ContextSource.MEMORY,
        priority=ContextPriority.HIGH,
        content="Test content",
        token_estimate=10,
        provenance=prov
    )
    section = ContextSection(source=ContextSource.MEMORY, priority=ContextPriority.HIGH, items=[item])
    
    result = validator.validate([section], policy)
    assert result.is_valid is False
    assert any("invalid confidence: 1.5" in e for e in result.errors)
    assert any("invalid ranking_score: -0.5" in e for e in result.errors)

def test_validator_token_sanity():
    validator = DefaultContextValidator()
    policy = ContextPolicy(policy_id="test", name="Test", enabled_providers=[ContextSource.MEMORY], token_budget=100)
    
    # 600 > 100 * 5
    section = ContextSection(source=ContextSource.MEMORY, priority=ContextPriority.HIGH, items=[], token_estimate=600)
    
    result = validator.validate([section], policy)
    assert result.is_valid is False
    assert any("exceeds sanity limit" in e for e in result.errors)

def test_validator_empty_citations_warning():
    validator = DefaultContextValidator()
    policy = ContextPolicy(policy_id="test", name="Test", enabled_providers=[ContextSource.MEMORY])
    
    item = create_mock_item(citations=["  "])
    section = ContextSection(source=ContextSource.MEMORY, priority=ContextPriority.HIGH, items=[item])
    
    result = validator.validate([section], policy)
    assert result.is_valid is True
    assert len(result.warnings) == 1
    assert "Empty citation found" in result.warnings[0]
