"""In-memory Token Budget Service for Wave 0.

Provides token budget enforcement using an in-memory dictionary cache.
This is used in Wave 0 before Supabase persistence is fully wired.
In Wave 1, this service will be replaced or extended to persist
TokenUsageRecord entries to the database for true accounting.
"""

from datetime import UTC, datetime
from typing import Any

import structlog

from app.infrastructure.ai.budgets.interfaces import IResourceBudget, ResourceBudgetType
from app.infrastructure.ai.budgets.models import BudgetPolicy, TokenBudget, TokenUsageRecord
from app.infrastructure.ai.models import BudgetExceededError

logger = structlog.get_logger(__name__)


class TokenBudgetService(IResourceBudget):
    """In-memory implementation of token budget enforcement."""

    def __init__(self) -> None:
        # entity_id -> TokenBudget
        self._budgets: dict[str, TokenBudget] = {}
        # entity_id -> list[TokenUsageRecord]
        self._records: dict[str, list[TokenUsageRecord]] = {}

        # Define a default fallback limit for entities without a configured budget
        # We set this high enough not to break tests, but low enough to enforce
        self._default_daily_limit = 500_000

    @property
    def budget_type(self) -> ResourceBudgetType:
        return ResourceBudgetType.TOKEN

    def _ensure_budget(self, entity_id: str) -> TokenBudget:
        """Get existing budget or create default for entity."""
        if entity_id not in self._budgets:
            self._budgets[entity_id] = TokenBudget(
                entity_id=entity_id,
                daily_limit=self._default_daily_limit,
                policy=BudgetPolicy.WARN,
            )
            self._records[entity_id] = []

        budget = self._budgets[entity_id]

        # Handle daily reset logic
        now = datetime.now(UTC)
        if budget.last_reset_date.date() < now.date():
            budget.current_day_usage = 0
            budget.last_reset_date = now

        return budget

    async def pre_check(self, entity_id: str, estimated_cost: int = 0) -> None:
        """Enforce budget limits before a request is executed."""
        budget = self._ensure_budget(entity_id)

        if budget.daily_limit is None:
            return  # Unlimited

        projected_usage = budget.current_day_usage + estimated_cost
        if projected_usage > budget.daily_limit:
            msg = f"Projected usage ({projected_usage}) exceeds daily limit ({budget.daily_limit})"

            if budget.policy == BudgetPolicy.HARD_STOP:
                raise BudgetExceededError(
                    entity_id=entity_id,
                    policy=budget.policy,
                    detail=msg,
                )
            elif budget.policy == BudgetPolicy.WARN:
                logger.warning(
                    "budget_limit_exceeded_warning",
                    entity_id=entity_id,
                    projected_usage=projected_usage,
                    daily_limit=budget.daily_limit,
                    budget_type=self.budget_type.value,
                )

    async def record_consumption(
        self,
        entity_id: str,
        lifecycle_id: str,
        amount: int,
        session_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Record tokens actually consumed by the provider."""
        budget = self._ensure_budget(entity_id)
        budget.current_day_usage += amount

        prompt_tokens = kwargs.get("prompt_tokens", 0)
        completion_tokens = kwargs.get("completion_tokens", 0)

        record = TokenUsageRecord(
            entity_id=entity_id,
            lifecycle_id=lifecycle_id,
            total_tokens=amount,
            prompt_tokens=prompt_tokens if isinstance(prompt_tokens, int) else 0,
            completion_tokens=completion_tokens if isinstance(completion_tokens, int) else 0,
            session_id=session_id,
        )
        self._records[entity_id].append(record)

        logger.debug(
            "budget_consumption_recorded",
            entity_id=entity_id,
            lifecycle_id=lifecycle_id,
            amount=amount,
            current_day_usage=budget.current_day_usage,
        )

    async def get_status(self, entity_id: str) -> TokenBudget:
        """Get the current budget status for an entity."""
        return self._ensure_budget(entity_id)

    def configure_budget(
        self, entity_id: str, daily_limit: int | None, policy: BudgetPolicy
    ) -> None:
        """Test/admin helper to manually set a budget configuration."""
        self._ensure_budget(entity_id)
        budget = self._budgets[entity_id]
        budget.daily_limit = daily_limit
        budget.policy = policy
