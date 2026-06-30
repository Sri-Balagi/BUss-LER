"""Domain models for the Resource Budget System.

Defines the core data structures for tracking and configuring budgets,
including the fundamental TokenBudget and TokenUsageRecord models,
as well as the BudgetPolicy enum for enforcement rules.
"""

from datetime import UTC, datetime
from enum import StrEnum
from pydantic import Field

from app.interfaces.http.schemas.base import DomainBaseModel


class BudgetPolicy(StrEnum):
    """Enforcement policy when a budget limit is reached."""

    HARD_STOP = "HARD_STOP"
    WARN = "WARN"
    DEGRADE = "DEGRADE"


class TokenBudget(DomainBaseModel):
    """Configuration and status of a token-based resource budget."""

    entity_id: str = Field(..., description="The entity this budget applies to.")
    daily_limit: int | None = Field(
        None, description="Maximum tokens allowed per day. None means unlimited."
    )
    session_limit: int | None = Field(
        None, description="Maximum tokens allowed per cognitive session. None means unlimited."
    )
    policy: BudgetPolicy = Field(
        default=BudgetPolicy.WARN,
        description="Action to take when a limit is exceeded.",
    )
    current_day_usage: int = Field(default=0, description="Tokens consumed so far today.")
    last_reset_date: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="The date this budget's daily usage was last reset to 0.",
    )


class TokenUsageRecord(DomainBaseModel):
    """Immutable record of tokens consumed by a single AI request."""

    entity_id: str = Field(..., description="The entity that consumed the tokens.")
    lifecycle_id: str = Field(
        ..., description="The AI Request Lifecycle ID associated with this usage."
    )
    prompt_tokens: int = Field(default=0, description="Input tokens consumed.")
    completion_tokens: int = Field(default=0, description="Output tokens consumed.")
    total_tokens: int = Field(default=0, description="Total tokens consumed.")
    session_id: str | None = Field(None, description="Cognitive session ID, if applicable.")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the tokens were consumed.",
    )
