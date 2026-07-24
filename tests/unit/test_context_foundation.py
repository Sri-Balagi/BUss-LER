import sys
from unittest.mock import MagicMock

# Mock structlog before importing
sys.modules["structlog"] = MagicMock()

import asyncio  # noqa: E402
from datetime import UTC, datetime, timezone  # noqa: E402
from uuid import uuid4  # noqa: E402

import pytest  # noqa: E402

from app.application.context.foundation.context_freshness import (  # noqa: E402
    DEFAULT_FRESHNESS_POLICIES,
    ContextFreshnessPolicy,
)
from app.application.context.foundation.context_policies import (  # noqa: E402
    BUILT_IN_POLICIES,
    ContextPolicy,
)
from app.platform.resilience.context_retry import (  # noqa: E402
    ProviderRetryConfig,
    provide_with_retry,
)
from app.shared.enums import ContextSource, RefreshStrategy  # noqa: E402


def test_context_freshness_import_and_logic():
    """Verify ContextFreshnessPolicy imports and basic logic."""
    policy = ContextFreshnessPolicy(
        provider=ContextSource.MEMORY,
        max_age_seconds=10,
        cache_ttl_seconds=20,
        refresh_strategy=RefreshStrategy.LAZY,
    )

    now = datetime.now(UTC)
    # Shouldn't be stale immediately
    assert not policy.is_stale(now)

    # Expiry
    expires = policy.expires_at(now)
    assert (expires - now).total_seconds() == 20


def test_context_policies_import_and_logic():
    """Verify ContextPolicy imports and factory methods."""
    planning = ContextPolicy.planning()
    assert planning.policy_id == "planning"
    assert ContextSource.GOAL in planning.required_providers
    assert planning.token_budget == 64_000

    recommendation = ContextPolicy.recommendation()
    assert recommendation.policy_id == "recommendation"
    assert recommendation.token_budget == 32_000

    assert "planning" in BUILT_IN_POLICIES
    assert "recommendation" in BUILT_IN_POLICIES


@pytest.mark.asyncio
async def test_context_retry_import_and_logic():
    """Verify ProviderRetryConfig imports and retry logic."""
    config = ProviderRetryConfig(
        timeout_seconds=0.1,
        max_retries=1,
        backoff_base=0.01,
        max_delay=0.1,
        jitter=False,
    )

    class MockProvider:
        def __init__(self):
            self.attempts = 0

        async def provide(self, ctx, twin_id, policy):
            self.attempts += 1
            if self.attempts == 1:
                raise ValueError("Temporary failure")
            return "Success"

    provider = MockProvider()

    result = await provide_with_retry(
        provider=provider,
        retry_config=config,
        ctx=MagicMock(),
        twin_id=uuid4(),
        policy=MagicMock(),
        source=ContextSource.MEMORY,
    )

    assert result == "Success"
    assert provider.attempts == 2
