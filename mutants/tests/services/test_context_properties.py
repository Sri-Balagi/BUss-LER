from datetime import UTC, datetime
from uuid import uuid4

import pytest
from app.models.enterprise_context import ContextItem, ContextProvenance, ContextSection
from app.models.enums import ContextPriority, ContextSource
from app.services.context_policies import ContextPolicy
from app.services.context_validators import DefaultContextValidator
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st


@pytest.fixture
def validator():
    return DefaultContextValidator()


@pytest.fixture
def policy():
    return ContextPolicy(
        policy_id="test", required_providers=[], enabled_providers=[], token_budget=1000
    )


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    confidence=st.floats(min_value=0.0, max_value=1.0),
    ranking_score=st.floats(min_value=0.0, max_value=1.0),
    token_estimate=st.integers(min_value=0, max_value=10000),
)
def test_validator_properties(validator, policy, confidence, ranking_score, token_estimate):
    # Context Validator should never crash on these inputs, just return valid or invalid
    prov = ContextProvenance(
        provider=ContextSource.MEMORY,
        service_name="test_service",
        source=ContextSource.MEMORY,
        confidence=confidence,
        ranking_score=ranking_score,
        citations=["valid"],
    )

    item = ContextItem(
        item_id=str(uuid4()),
        source=ContextSource.MEMORY,
        priority=ContextPriority.MEDIUM,
        content="data",
        content_type="memory",
        token_estimate=max(0, token_estimate),  # Item token estimate usually >= 0 natively
        provenance=prov,
    )

    section = ContextSection(
        source=ContextSource.MEMORY,
        items=[item],
        token_estimate=token_estimate,
        retrieved_at=datetime.now(UTC),
    )

    result = validator.validate([section], policy)

    if token_estimate > policy.token_budget * 5:
        assert result.is_valid is False
    else:
        assert result.is_valid is True
