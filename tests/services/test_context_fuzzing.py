import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.services.context_engine import ContextEngine
from app.core.context import OperationContext
from app.models.enterprise_context import EnterpriseContextCreate


@pytest.fixture
def op_ctx():
    return OperationContext(correlation_id="fuzz-test")


@pytest.fixture
def engine():
    # Provide dummy dependencies
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

    # Mock internal methods to avoid running the whole pipeline
    async def mock_execute(*args, **kwargs):
        await asyncio.sleep(0.01)  # Simulate async IO
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

    # Mock policy lookup
    from app.services.context_policies import ContextPolicy

    mock_policy = ContextPolicy(
        policy_id="test_policy",
        required_providers=[],
        enabled_providers=[],
        token_budget=1000,
    )
    import app.services.context_engine as ce

    ce.BUILT_IN_POLICIES["test_policy"] = mock_policy

    # Mock graph resolve
    mock_graph.resolve.return_value = MagicMock(total_providers=0, batches=[])

    return e


@pytest.mark.asyncio
async def test_concurrent_context_building(engine, op_ctx):
    twin_id = uuid4()
    command = EnterpriseContextCreate(
        twin_id=twin_id, policy_id="test_policy", intent_id=uuid4()
    )

    # Fire 50 requests concurrently
    tasks = [engine.build(ctx=op_ctx, command=command) for _ in range(50)]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in results:
        assert not isinstance(result, Exception), f"Failed with {result}"
        assert result.context_id is not None
        assert result.twin_id == twin_id

    # We did 50 builds
    assert engine._execute_providers.call_count == 50
