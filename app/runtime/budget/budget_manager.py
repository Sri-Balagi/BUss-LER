from app.runtime.core.exceptions import BudgetExceededError
from app.runtime.interfaces.budget import IExecutionBudget


class BudgetManager:
    """
    Tracks and enforces budget limits independently of the ExecutionSession.
    """
    def __init__(self, budget: IExecutionBudget):
        self._budget = budget
        self._tokens_consumed = 0
        self._time_elapsed_ms = 0
        self._retries_used = 0
        self._cost_incurred_cents = 0

    def consume_tokens(self, amount: int) -> None:
        if self._tokens_consumed + amount > self._budget.max_tokens:
            raise BudgetExceededError(
                resource_type="tokens",
                limit=self._budget.max_tokens,
                actual=self._tokens_consumed + amount
            )
        self._tokens_consumed += amount

    def consume_time(self, ms: int) -> None:
        if self._time_elapsed_ms + ms > self._budget.max_time_ms:
            raise BudgetExceededError(
                resource_type="time_ms",
                limit=self._budget.max_time_ms,
                actual=self._time_elapsed_ms + ms
            )
        self._time_elapsed_ms += ms

    def consume_retry(self) -> None:
        if self._retries_used + 1 > self._budget.max_retries:
            raise BudgetExceededError(
                resource_type="retries",
                limit=self._budget.max_retries,
                actual=self._retries_used + 1
            )
        self._retries_used += 1

    @property
    def tokens_consumed(self) -> int:
        return self._tokens_consumed
