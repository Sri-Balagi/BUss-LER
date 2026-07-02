import pytest

from app.runtime.budget.budget_manager import BudgetManager
from app.runtime.budget.execution_budget import ExecutionBudget
from app.runtime.core.exceptions import BudgetExceededError


def test_budget_manager_initialization():
    budget = ExecutionBudget(token_limit=100, time_limit_ms=200, retry_limit=2)
    manager = BudgetManager(budget)
    assert manager.tokens_consumed == 0


def test_budget_manager_token_consumption():
    budget = ExecutionBudget(token_limit=100)
    manager = BudgetManager(budget)

    manager.consume_tokens(50)
    assert manager.tokens_consumed == 50

    manager.consume_tokens(50)
    assert manager.tokens_consumed == 100

    with pytest.raises(BudgetExceededError):
        manager.consume_tokens(1)


def test_budget_manager_time_consumption():
    budget = ExecutionBudget(time_limit_ms=100)
    manager = BudgetManager(budget)
    manager.consume_time(90)

    with pytest.raises(BudgetExceededError):
        manager.consume_time(11)


def test_budget_manager_retry_consumption():
    budget = ExecutionBudget(retry_limit=1)
    manager = BudgetManager(budget)

    manager.consume_retry()

    with pytest.raises(BudgetExceededError):
        manager.consume_retry()
