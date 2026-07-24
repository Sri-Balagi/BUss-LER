from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from app.models.enums import ContextSource
from app.services.context_policies import BUILT_IN_POLICIES
from app.services.context_providers.business_state_provider import (
    BusinessStateContextProvider,
)
from app.services.context_providers.conversation_provider import (
    ConversationContextProvider,
)
from app.services.context_providers.external_provider import (
    ExternalIntegrationContextProvider,
)
from app.services.context_providers.goal_provider import GoalContextProvider
from app.services.context_providers.intent_provider import IntentContextProvider

# Import all providers
from app.services.context_providers.memory_provider import MemoryContextProvider
from app.services.context_providers.plan_provider import PlanContextProvider
from app.services.context_providers.recommendation_provider import (
    RecommendationContextProvider,
)
from app.services.context_providers.trace_provider import TraceContextProvider
from app.services.context_providers.twin_provider import TwinContextProvider

from app.core.context import OperationContext


@pytest.fixture
def ctx():
    return OperationContext(request_id="req1", correlation_id="cor1", user_id=uuid4())


@pytest.fixture
def policy():
    return BUILT_IN_POLICIES["planning"]


@pytest.mark.asyncio
async def test_memory_provider_exception(ctx, policy):
    service = AsyncMock()
    service.search_memories.side_effect = Exception("db error")
    service.health_check.side_effect = Exception("hc error")

    provider = MemoryContextProvider(service)

    # provide
    section = await provider.provide(ctx, uuid4(), policy)
    assert section.source == ContextSource.MEMORY
    assert len(section.items) == 0

    # health check
    hc = await provider.health_check()
    assert hc["memory_context_provider"] == "error"


@pytest.mark.asyncio
async def test_goal_provider_exception(ctx, policy):
    service = AsyncMock()
    service.get_active_goals.side_effect = Exception("db error")
    service.health_check.side_effect = Exception("hc error")

    provider = GoalContextProvider(service)

    section = await provider.provide(ctx, uuid4(), policy)
    assert section.source == ContextSource.GOAL
    assert len(section.items) == 0

    hc = await provider.health_check()
    assert hc["goal_context_provider"] == "ok"


@pytest.mark.asyncio
async def test_intent_provider_exception(ctx, policy):
    service = AsyncMock()
    service.get_intents_for_twin.side_effect = Exception("db error")
    service.health_check.side_effect = Exception("hc error")

    provider = IntentContextProvider(service)

    section = await provider.provide(ctx, uuid4(), policy)
    assert section.source == ContextSource.INTENT
    assert len(section.items) == 0

    hc = await provider.health_check()
    assert hc["intent_context_provider"] == "ok"


@pytest.mark.asyncio
async def test_plan_provider_exception(ctx, policy):
    service = AsyncMock()
    service.get_active_plans.side_effect = Exception("db error")
    service.health_check.side_effect = Exception("hc error")

    provider = PlanContextProvider(service)

    section = await provider.provide(ctx, uuid4(), policy)
    assert section.source == ContextSource.PLAN
    assert len(section.items) == 0

    hc = await provider.health_check()
    assert hc["plan_context_provider"] == "ok"


@pytest.mark.asyncio
async def test_recommendation_provider_exception(ctx, policy):
    service = AsyncMock()
    service.get_active_recommendations.side_effect = Exception("db error")
    service.health_check.side_effect = Exception("hc error")

    provider = RecommendationContextProvider(service)

    section = await provider.provide(ctx, uuid4(), policy)
    assert section.source == ContextSource.RECOMMENDATION
    assert len(section.items) == 0

    hc = await provider.health_check()
    assert hc["recommendation_context_provider"] == "ok"


@pytest.mark.asyncio
async def test_twin_provider_exception(ctx, policy):
    service = AsyncMock()
    service.get_twin.side_effect = Exception("db error")
    service.health_check.side_effect = Exception("hc error")

    provider = TwinContextProvider(service)

    section = await provider.provide(ctx, uuid4(), policy)
    assert section.source == ContextSource.TWIN
    assert len(section.items) == 0

    hc = await provider.health_check()
    assert hc["twin_context_provider"] == "ok"


@pytest.mark.asyncio
async def test_business_state_provider_exception(ctx, policy):
    service = AsyncMock()
    service.get_state = AsyncMock(side_effect=Exception("db error"))
    service.health_check.side_effect = Exception("hc error")

    provider = BusinessStateContextProvider(service)

    section = await provider.provide(ctx, uuid4(), policy)
    assert section.source == ContextSource.BUSINESS_STATE
    assert len(section.items) == 0

    hc = await provider.health_check()
    assert hc["business_state_context_provider"] == "ok"


@pytest.mark.asyncio
async def test_conversation_provider_exception(ctx, policy):
    service = AsyncMock()
    service.get_recent_turns.side_effect = Exception("db error")
    service.health_check.side_effect = Exception("hc error")

    provider = ConversationContextProvider(service)

    section = await provider.provide(ctx, uuid4(), policy)
    assert section.source == ContextSource.CONVERSATION
    assert len(section.items) == 0

    hc = await provider.health_check()
    assert hc["conversation_context_provider"] == "error"


@pytest.mark.asyncio
async def test_trace_provider_exception(ctx, policy):
    service = AsyncMock()
    service.get_recent_traces.side_effect = Exception("db error")
    service.health_check.side_effect = Exception("hc error")

    provider = TraceContextProvider(service)

    section = await provider.provide(ctx, uuid4(), policy)
    assert section.source == ContextSource.TRACE
    assert len(section.items) == 0

    hc = await provider.health_check()
    assert hc["trace_context_provider"] == "ok"


@pytest.mark.asyncio
async def test_external_provider_exception(ctx, policy):
    service = AsyncMock()
    service.fetch_data.side_effect = Exception("api error")
    service.health_check.side_effect = Exception("hc error")

    provider = ExternalIntegrationContextProvider()

    section = await provider.provide(ctx, uuid4(), policy)
    assert section.source == ContextSource.EXTERNAL
    assert len(section.items) == 0

    hc = await provider.health_check()
    assert hc["external_context_provider"] == "ok_stub"


@pytest.mark.asyncio
async def test_memory_provider_happy(ctx, policy):
    service = AsyncMock()
    mock_item = MagicMock()
    mock_item.memory.id = uuid4()
    mock_item.memory.content = "test memory content"
    mock_item.similarity_score = 0.95

    mock_result = MagicMock()
    mock_result.items = [mock_item]
    service.search_memories.return_value = mock_result

    provider = MemoryContextProvider(service)
    section = await provider.provide(ctx, uuid4(), policy)
    assert section.source == ContextSource.MEMORY
    assert len(section.items) == 1
    assert section.items[0].content == "test memory content"


@pytest.mark.asyncio
async def test_goal_provider_happy(ctx, policy):
    service = AsyncMock()
    mock_goal = MagicMock()
    mock_goal.id = uuid4()
    mock_goal.title = "test goal"
    mock_goal.description = "desc"
    mock_goal.status.value = "active"
    mock_goal.priority.value = "high"
    service.get_active_goals.return_value = [mock_goal]

    provider = GoalContextProvider(service)
    section = await provider.provide(ctx, uuid4(), policy)
    assert section.source == ContextSource.GOAL
    assert len(section.items) == 1
    assert "test goal" in section.items[0].content


    section = await provider.provide(ctx, uuid4(), policy)
    assert section.source == ContextSource.GOAL
    assert len(section.items) == 1
    assert "test goal" in section.items[0].content


@pytest.mark.asyncio
async def test_intent_provider_happy(ctx, policy):
    service = AsyncMock()
    mock_intent = MagicMock()
    mock_intent.id = uuid4()
    mock_intent.raw_text = "test intent"
    mock_intent.description = "desc"
    mock_intent.status.value = "active"
    mock_result = MagicMock()
    mock_result.items = [mock_intent]
    service.list_intents.return_value = mock_result

    provider = IntentContextProvider(service)
    section = await provider.provide(ctx, uuid4(), policy)
    assert section.source == ContextSource.INTENT
    assert len(section.items) == 1
    assert "test intent" in section.items[0].content


@pytest.mark.asyncio
async def test_plan_provider_happy(ctx, policy):
    service = AsyncMock()
    mock_plan = MagicMock()
    mock_plan.id = uuid4()
    mock_plan.title = "test plan"
    mock_plan.description = "desc"
    mock_plan.status.value = "active"
    mock_result = MagicMock()
    mock_result.items = [mock_plan]
    service.list_plans.return_value = mock_result

    provider = PlanContextProvider(service)
    section = await provider.provide(ctx, uuid4(), policy)
    assert section.source == ContextSource.PLAN
    assert len(section.items) == 1
    assert "test plan" in section.items[0].content


@pytest.mark.asyncio
async def test_recommendation_provider_happy(ctx, policy):
    service = AsyncMock()
    mock_rec = MagicMock()
    mock_rec.id = uuid4()
    mock_rec.title = "test rec"
    mock_rec.description = "desc"
    mock_rec.priority.value = "high"
    mock_result = MagicMock()
    mock_result.items = [mock_rec]
    service.list_recommendations.return_value = mock_result

    provider = RecommendationContextProvider(service)
    section = await provider.provide(ctx, uuid4(), policy)
    assert section.source == ContextSource.RECOMMENDATION
    assert len(section.items) == 1
    assert "test rec" in section.items[0].content


@pytest.mark.asyncio
async def test_twin_provider_happy(ctx, policy):
    service = AsyncMock()
    mock_twin = MagicMock()
    mock_twin.id = uuid4()
    mock_twin.name = "test twin"
    mock_twin.description = "desc"
    mock_twin.system_prompt = "sys prompt"
    service.get_twin.return_value = mock_twin

    provider = TwinContextProvider(service)
    section = await provider.provide(ctx, uuid4(), policy)
    assert section.source == ContextSource.TWIN


@pytest.mark.asyncio
async def test_conversation_provider_happy(ctx, policy):
    service = AsyncMock()
    mock_turn = MagicMock()
    mock_turn.id = uuid4()
    mock_turn.role.value = "user"
    mock_turn.content = "test msg"
    service.get_recent_turns.return_value = [mock_turn]

    provider = ConversationContextProvider(service)
    section = await provider.provide(ctx, uuid4(), policy)
    assert section.source == ContextSource.CONVERSATION
    assert len(section.items) == 1
    assert "test msg" in section.items[0].content


@pytest.mark.asyncio
async def test_trace_provider_happy(ctx, policy):
    service = AsyncMock()
    mock_trace = MagicMock()
    mock_trace.id = uuid4()
    mock_trace.operation_type = "reasoning"
    mock_trace.provider_name = "test_provider"
    mock_trace.status.value = "success"
    mock_trace.duration_ms = 100
    mock_trace.output_data = {"result": "ok"}
    mock_result = MagicMock()
    mock_result.items = [mock_trace]
    service.list_traces.return_value = mock_result

    policy.include_traces = True

    provider = TraceContextProvider(service)
    section = await provider.provide(ctx, uuid4(), policy)
    assert section.source == ContextSource.TRACE
    assert len(section.items) == 1
    assert "reasoning" in section.items[0].content


@pytest.mark.asyncio
async def test_business_state_provider_happy(ctx, policy):
    service = AsyncMock()
    mock_twin = MagicMock()
    mock_twin.id = uuid4()
    mock_twin.state = {"sales": {"revenue": 1000}, "marketing": {"clicks": 500}}
    service.get_twin = AsyncMock(return_value=mock_twin)

    provider = BusinessStateContextProvider(service)
    section = await provider.provide(ctx, uuid4(), policy)
    assert section.source == ContextSource.BUSINESS_STATE
    assert len(section.items) == 2
