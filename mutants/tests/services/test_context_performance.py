import asyncio
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from app.models.enterprise_context import EnterpriseContextCreate
from app.services.context_engine import ContextEngine

from app.core.context import OperationContext


@pytest.fixture
def engine():
    mock_registry = MagicMock()
    mock_graph = MagicMock()
    mock_validator = MagicMock()
    mock_ranker = MagicMock()
    mock_compressor = MagicMock()
    mock_window_builder = MagicMock()

    e = ContextEngine(
        provider_registry=mock_registry,
        dependency_graph=mock_graph,
        validator=mock_validator,
        ranker=mock_ranker,
        compressor=mock_compressor,
        window_builder=mock_window_builder,
    )

    async def mock_execute(*args, **kwargs):
        return [], [], {}

    e._execute_providers = AsyncMock(side_effect=mock_execute)
    e._validate = MagicMock()
    e._rank = MagicMock(return_value=([], 0.0))
    e._compress = MagicMock(return_value=([], 0.0, 1.0, 0, 0, 0, 0))
    from app.models.enterprise_context import ContextWindow

    e._build_window = MagicMock(
        return_value=(
            ContextWindow(
                window_id=uuid4(),
                sections=[],
                token_estimate=0,
                budget=1000,
                items_included=0,
                items_excluded=0,
                overflow=False,
            ),
            0.0,
        )
    )

    import app.services.context_engine as ce
    from app.services.context_policies import ContextPolicy

    ce.BUILT_IN_POLICIES["perf_policy"] = ContextPolicy(
        policy_id="perf_policy",
        required_providers=[],
        enabled_providers=[],
        token_budget=1000,
    )
    mock_graph.resolve.return_value = MagicMock(total_providers=0, batches=[])

    return e


def test_context_engine_performance(benchmark, engine):
    op_ctx = OperationContext(correlation_id="perf-test")
    twin_id = uuid4()
    command = EnterpriseContextCreate(twin_id=twin_id, policy_id="perf_policy")

    def run_build():
        return asyncio.run(engine.build(ctx=op_ctx, command=command))

    result = benchmark(run_build)
    assert result is not None
