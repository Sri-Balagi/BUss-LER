"""Tests for the Resource Budget System — WP-02."""

from datetime import UTC, datetime, timedelta

import pytest
import structlog
from structlog.testing import capture_logs

from app.infrastructure.ai.budgets.interfaces import ResourceBudgetType
from app.infrastructure.ai.budgets.models import BudgetPolicy, TokenBudget
from app.infrastructure.ai.budgets.token_budget_service import TokenBudgetService
from app.infrastructure.ai.models import BudgetExceededError


@pytest.fixture
def budget_service() -> TokenBudgetService:
    return TokenBudgetService()


@pytest.mark.asyncio
async def test_budget_type(budget_service: TokenBudgetService) -> None:
    assert budget_service.budget_type == ResourceBudgetType.TOKEN


@pytest.mark.asyncio
async def test_ensure_budget_creates_default(budget_service: TokenBudgetService) -> None:
    budget = await budget_service.get_status("new-entity")
    assert budget.entity_id == "new-entity"
    assert budget.daily_limit == 500_000
    assert budget.policy == BudgetPolicy.WARN
    assert budget.current_day_usage == 0


@pytest.mark.asyncio
async def test_configure_budget(budget_service: TokenBudgetService) -> None:
    budget_service.configure_budget("entity-1", daily_limit=1000, policy=BudgetPolicy.HARD_STOP)
    budget = await budget_service.get_status("entity-1")
    assert budget.daily_limit == 1000
    assert budget.policy == BudgetPolicy.HARD_STOP


@pytest.mark.asyncio
async def test_pre_check_hard_stop_raises(budget_service: TokenBudgetService) -> None:
    budget_service.configure_budget("entity-1", daily_limit=100, policy=BudgetPolicy.HARD_STOP)

    # Should not raise
    await budget_service.pre_check("entity-1", estimated_cost=90)

    # Should raise
    with pytest.raises(BudgetExceededError) as exc_info:
        await budget_service.pre_check("entity-1", estimated_cost=110)
    assert exc_info.value.entity_id == "entity-1"
    assert exc_info.value.policy == BudgetPolicy.HARD_STOP


@pytest.mark.asyncio
async def test_pre_check_warn_logs_does_not_raise(budget_service: TokenBudgetService) -> None:
    budget_service.configure_budget("entity-1", daily_limit=100, policy=BudgetPolicy.WARN)

    # Configure structlog to capture logs
    with capture_logs() as cap_logs:
        await budget_service.pre_check("entity-1", estimated_cost=150)

    assert len(cap_logs) == 1
    assert cap_logs[0]["event"] == "budget_limit_exceeded_warning"
    assert cap_logs[0]["entity_id"] == "entity-1"
    assert cap_logs[0]["projected_usage"] == 150


@pytest.mark.asyncio
async def test_pre_check_unlimited_budget(budget_service: TokenBudgetService) -> None:
    budget_service.configure_budget("entity-1", daily_limit=None, policy=BudgetPolicy.HARD_STOP)

    # Should never raise since daily_limit is None
    await budget_service.pre_check("entity-1", estimated_cost=1_000_000)


@pytest.mark.asyncio
async def test_record_consumption_accumulates(budget_service: TokenBudgetService) -> None:
    await budget_service.record_consumption(
        entity_id="entity-1",
        lifecycle_id="lc-1",
        amount=100,
        prompt_tokens=40,
        completion_tokens=60,
    )

    budget = await budget_service.get_status("entity-1")
    assert budget.current_day_usage == 100

    await budget_service.record_consumption(entity_id="entity-1", lifecycle_id="lc-2", amount=50)

    budget = await budget_service.get_status("entity-1")
    assert budget.current_day_usage == 150

    # Verify the records list
    records = budget_service._records["entity-1"]
    assert len(records) == 2
    assert records[0].lifecycle_id == "lc-1"
    assert records[0].prompt_tokens == 40
    assert records[1].lifecycle_id == "lc-2"


@pytest.mark.asyncio
async def test_daily_reset_logic(budget_service: TokenBudgetService) -> None:
    # Setup initial consumption
    await budget_service.record_consumption("entity-1", "lc-1", 100)
    budget = await budget_service.get_status("entity-1")
    assert budget.current_day_usage == 100

    # Backdate the last_reset_date to yesterday
    yesterday = datetime.now(UTC) - timedelta(days=1)
    budget.last_reset_date = yesterday

    # Now when we query or update, it should reset to 0
    budget = await budget_service.get_status("entity-1")
    assert budget.current_day_usage == 0

    # Add new consumption
    await budget_service.record_consumption("entity-1", "lc-2", 50)
    budget = await budget_service.get_status("entity-1")
    assert budget.current_day_usage == 50
