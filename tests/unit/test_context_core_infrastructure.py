import sys
from unittest.mock import MagicMock

# Mock structlog due to missing dependency in test environment
if "structlog" not in sys.modules:
    sys.modules["structlog"] = MagicMock()

from datetime import UTC, datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.application.context.dependency_graph import ContextDependencyGraph
from app.application.context.foundation.context_policies import ContextPolicy
from app.application.context.state import ContextStateMachine
from app.application.context.strategies import (
    DefaultContextCompressor,
    DefaultContextRanker,
    DefaultContextWindowBuilder,
)
from app.application.context.validators import DefaultContextValidator
from app.intelligence.intake.situation.enterprise_context import (
    ContextItem,
    ContextProvenance,
    ContextSection,
    ProviderDependency,
)
from app.shared.enums import ContextPriority, ContextSource, ContextStatus
from app.shared.exceptions.errors import ContextDependencyCycleError, InvalidStateTransitionError


def test_context_state_machine():
    # Valid transitions
    assert ContextStatus.ASSEMBLED in ContextStateMachine.allowed_next(ContextStatus.BUILDING)
    ContextStateMachine.validate_transition(ContextStatus.BUILDING, ContextStatus.ASSEMBLED)

    # Terminal state
    assert ContextStateMachine.is_terminal(ContextStatus.ARCHIVED)

    # Invalid transition
    with pytest.raises(InvalidStateTransitionError):
        ContextStateMachine.validate_transition(ContextStatus.BUILDING, ContextStatus.CONSUMED)


def test_context_dependency_graph():
    graph = ContextDependencyGraph()
    graph.register(
        ProviderDependency(provider=ContextSource.CONVERSATION, depends_on=[ContextSource.TWIN])
    )

    # Cyclic dependency should raise error
    with pytest.raises(ContextDependencyCycleError):
        graph.register(
            ProviderDependency(provider=ContextSource.TWIN, depends_on=[ContextSource.CONVERSATION])
        )

    # Valid resolution on a new graph
    valid_graph = ContextDependencyGraph()
    valid_graph.register(
        ProviderDependency(provider=ContextSource.CONVERSATION, depends_on=[ContextSource.TWIN])
    )
    plan = valid_graph.resolve([ContextSource.TWIN, ContextSource.CONVERSATION])
    assert len(plan.batches) == 2
    assert plan.batches[0] == [ContextSource.TWIN]
    assert plan.batches[1] == [ContextSource.CONVERSATION]


def test_context_validators():
    validator = DefaultContextValidator()
    policy = ContextPolicy.agent()

    # Missing GOAL which is required in agent policy
    res = validator.validate([], policy)
    assert not res.is_valid
    assert any("GOAL" in e for e in res.errors)

    # Valid sections
    prov = ContextProvenance(
        provider=ContextSource.GOAL, service_name="test", confidence=1.0, ranking_score=1.0
    )
    item = ContextItem(
        item_id=uuid4(),
        source=ContextSource.GOAL,
        priority=ContextPriority.CRITICAL,
        content="goal",
        content_type="text",
        token_estimate=10,
        provenance=prov,
    )
    section = ContextSection(
        source=ContextSource.GOAL, items=[item], token_estimate=10, retrieved_at=datetime.now(UTC)
    )

    prov2 = ContextProvenance(
        provider=ContextSource.INTENT, service_name="test", confidence=1.0, ranking_score=1.0
    )
    item2 = ContextItem(
        item_id=uuid4(),
        source=ContextSource.INTENT,
        priority=ContextPriority.CRITICAL,
        content="intent",
        content_type="text",
        token_estimate=10,
        provenance=prov2,
    )
    section2 = ContextSection(
        source=ContextSource.INTENT,
        items=[item2],
        token_estimate=10,
        retrieved_at=datetime.now(UTC),
    )

    res = validator.validate([section, section2], policy)
    assert res.is_valid


def test_context_strategies_ranker():
    ranker = DefaultContextRanker()
    prov = ContextProvenance(
        provider=ContextSource.MEMORY, service_name="test", confidence=0.8, ranking_score=0.0
    )
    item = ContextItem(
        item_id=uuid4(),
        source=ContextSource.MEMORY,
        priority=ContextPriority.HIGH,
        content="text",
        content_type="text",
        token_estimate=10,
        provenance=prov,
    )
    section = ContextSection(
        source=ContextSource.MEMORY, items=[item], token_estimate=10, retrieved_at=datetime.now(UTC)
    )

    policy = ContextPolicy.agent()
    ranked = ranker.rank([section], policy)
    assert len(ranked) == 1
    assert ranked[0].items[0].provenance.ranking_score > 0.0


def test_context_strategies_compressor():
    compressor = DefaultContextCompressor()
    prov = ContextProvenance(
        provider=ContextSource.MEMORY, service_name="test", confidence=0.8, ranking_score=0.5
    )
    item1 = ContextItem(
        item_id=uuid4(),
        source=ContextSource.MEMORY,
        priority=ContextPriority.BACKGROUND,
        content="text",
        content_type="text",
        token_estimate=10,
        provenance=prov,
    )
    item2 = ContextItem(
        item_id=uuid4(),
        source=ContextSource.MEMORY,
        priority=ContextPriority.BACKGROUND,
        content="text",
        content_type="text",
        token_estimate=10,
        provenance=prov,
    )
    item3 = ContextItem(
        item_id=uuid4(),
        source=ContextSource.MEMORY,
        priority=ContextPriority.BACKGROUND,
        content="text",
        content_type="text",
        token_estimate=10,
        provenance=prov,
    )
    item4 = ContextItem(
        item_id=uuid4(),
        source=ContextSource.MEMORY,
        priority=ContextPriority.BACKGROUND,
        content="text",
        content_type="text",
        token_estimate=10,
        provenance=prov,
    )

    # identical fingerprints -> deduplicated to 1 item
    section = ContextSection(
        source=ContextSource.MEMORY,
        items=[item1, item2, item3, item4],
        token_estimate=40,
        retrieved_at=datetime.now(UTC),
    )
    compressed = compressor.compress([section], budget=100)
    assert len(compressed[0].items) == 1


def test_context_strategies_window_builder():
    builder = DefaultContextWindowBuilder()
    prov = ContextProvenance(
        provider=ContextSource.GOAL, service_name="test", confidence=1.0, ranking_score=1.0
    )
    item = ContextItem(
        item_id=uuid4(),
        source=ContextSource.GOAL,
        priority=ContextPriority.CRITICAL,
        content="goal",
        content_type="text",
        token_estimate=10,
        provenance=prov,
    )
    section = ContextSection(
        source=ContextSource.GOAL, items=[item], token_estimate=10, retrieved_at=datetime.now(UTC)
    )

    window = builder.build_window([section], budget=5)
    # Budget 5 is less than cost 10, so it will be excluded
    assert window.items_excluded == 1
    assert window.overflow is True
