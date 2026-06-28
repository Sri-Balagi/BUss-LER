import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.models.enterprise_context import ContextItem, ContextProvenance, ContextSection
from app.models.enums import ContextPriority, ContextSource
from app.services.context_policies import BUILT_IN_POLICIES
from app.services.context_validators import DefaultContextValidator

@pytest.fixture
def validator():
    return DefaultContextValidator()

@pytest.fixture
def policy():
    return BUILT_IN_POLICIES["planning"]

def create_valid_section(source: ContextSource, item_count: int = 1) -> ContextSection:
    items = []
    for _ in range(item_count):
        prov = ContextProvenance(
            provider=source,
            service_name="TestService",
            retrieval_timestamp=datetime.now(timezone.utc),
            confidence=0.8,
            ranking_score=0.5,
            citations=["doc1"]
        )
        items.append(
            ContextItem(
                item_id=uuid4(),
                source=source,
                priority=ContextPriority.HIGH,
                content="test content",
                domain_object_id=uuid4(),
                token_estimate=10,
                provenance=prov
            )
        )
    return ContextSection(
        section_id=uuid4(),
        source=source,
        priority=ContextPriority.HIGH,
        items=items,
        token_estimate=item_count * 10,
        retrieved_at=datetime.now(timezone.utc)
    )

def test_valid_context(validator, policy):
    sections = [create_valid_section(ContextSource.GOAL)]
    result = validator.validate(sections, policy)
    assert result.is_valid is True
    assert not result.errors
    assert not result.warnings

def test_missing_required_provider(validator, policy):
    # Planning policy requires GOAL, we give it INTENT
    sections = [create_valid_section(ContextSource.INTENT)]
    result = validator.validate(sections, policy)
    assert result.is_valid is False
    assert any("has no section in assembled context" in err for err in result.errors)
    assert any("GOAL is required by policy but no active goals were found" in err for err in result.errors)

def test_duplicate_item_id(validator, policy):
    section1 = create_valid_section(ContextSource.GOAL)
    section2 = create_valid_section(ContextSource.INTENT)
    section2.items[0].item_id = section1.items[0].item_id
    
    sections = [section1, section2]
    result = validator.validate(sections, policy)
    # duplicate item is a warning, not error, so it's valid if goal is present
    assert result.is_valid is True
    assert any("Duplicate ContextItem ID" in warn for warn in result.warnings)

def test_missing_provenance(validator, policy):
    section = create_valid_section(ContextSource.GOAL)
    section.items[0].provenance = None
    
    result = validator.validate([section], policy)
    assert result.is_valid is False
    assert any("is missing ContextProvenance" in err for err in result.errors)

def test_empty_citation(validator, policy):
    section = create_valid_section(ContextSource.GOAL)
    section.items[0].provenance.citations = [""]
    
    result = validator.validate([section], policy)
    assert result.is_valid is True
    assert any("Empty citation found" in warn for warn in result.warnings)

def test_future_retrieved_at(validator, policy):
    section = create_valid_section(ContextSource.GOAL)
    section.retrieved_at = datetime.now(timezone.utc) + timedelta(days=1)
    
    result = validator.validate([section], policy)
    assert result.is_valid is False
    assert any("has a future retrieved_at timestamp" in err for err in result.errors)

def test_token_estimation_sanity_too_large(validator, policy):
    section = create_valid_section(ContextSource.GOAL)
    # Budget for planning is usually 4000
    section.token_estimate = policy.token_budget * 6
    
    result = validator.validate([section], policy)
    assert result.is_valid is False
    assert any("exceeds sanity limit" in err for err in result.errors)

def test_token_estimation_sanity_negative(validator, policy):
    section = create_valid_section(ContextSource.GOAL)
    section.token_estimate = -10
    
    result = validator.validate([section], policy)
    assert result.is_valid is False
    assert any("is negative" in err for err in result.errors)

def test_invalid_confidence_and_ranking(validator, policy):
    section = create_valid_section(ContextSource.GOAL)
    section.items[0].provenance.confidence = 1.5
    section.items[0].provenance.ranking_score = -0.5
    
    result = validator.validate([section], policy)
    assert result.is_valid is False
    assert any("has invalid confidence" in err for err in result.errors)
    assert any("has invalid ranking_score" in err for err in result.errors)

def test_critical_section_empty(validator, policy):
    section = create_valid_section(ContextSource.GOAL, item_count=0)
    
    result = validator.validate([section], policy)
    assert result.is_valid is False
    assert any("GOAL is required by policy but no active goals were found" in err for err in result.errors)
