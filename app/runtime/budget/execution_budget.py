from pydantic import BaseModel, Field

from app.runtime.interfaces.budget import IExecutionBudget


class ExecutionBudget(BaseModel, IExecutionBudget):
    """
    Concrete implementation of execution limits.
    """

    token_limit: int = Field(default=128000)
    time_limit_ms: int = Field(default=300000)
    recursion_depth_limit: int = Field(default=5)
    retry_limit: int = Field(default=3)
    cost_limit_cents: int = Field(default=100)

    @property
    def max_tokens(self) -> int:
        return self.token_limit

    @property
    def max_time_ms(self) -> int:
        return self.time_limit_ms

    @property
    def max_recursion_depth(self) -> int:
        return self.recursion_depth_limit

    @property
    def max_retries(self) -> int:
        return self.retry_limit

    @property
    def max_cost_cents(self) -> int:
        return self.cost_limit_cents
