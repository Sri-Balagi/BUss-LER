from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.application.context.engine import ContextAssemblyError, ContextEngine
from app.core.context import OperationContext
from app.intelligence.intake.situation.enterprise_context import (
    ContextSection,
    ContextWindow,
    EnterpriseContextCreate,
    ProviderFailureRecord,
)
from app.shared.enums import ContextSource, ContextStatus


@pytest.fixture
def ctx():
    return OperationContext(correlation_id="test-corr-id")

@pytest.fixture
def command():
    return EnterpriseContextCreate(
        twin_id=uuid4(),
        policy_id="planning",
        trigger_context={"query": "test"}
    )

@pytest.fixture
def engine():
    registry = MagicMock()
    graph = MagicMock()
    validator = MagicMock()
    ranker = MagicMock()
    compressor = MagicMock()
    window_builder = MagicMock()
    repository = AsyncMock()
    event_bus = AsyncMock()
    trace_service = AsyncMock()

    # Setup mocks
    graph.resolve.return_value = MagicMock(total_providers=1, providers={"test_provider": MagicMock()})

    engine = ContextEngine(
        provider_registry=registry,
        dependency_graph=graph,
        validator=validator,
        ranker=ranker,
        compressor=compressor,
        window_builder=window_builder,
        repository=repository,
        event_bus=event_bus,
        trace_service=trace_service
    )

    # Mock internal methods to isolate testing of the build flow
    engine._execute_providers = AsyncMock(return_value=([
        ContextSection(
            source=ContextSource.TWIN,
            items=[],
            provider_latency_ms=10.0,
            token_estimate=10
        )
    ], [], {"test_provider": 10.0}))

    engine._validate = MagicMock()
    engine._rank = MagicMock(return_value=([
        ContextSection(
            source=ContextSource.TWIN,
            items=[],
            provider_latency_ms=10.0,
            token_estimate=10
        )
    ], 5.0))

    engine._compress = MagicMock(return_value=(
        [], # compressed sections
        10.0, # comp latency
        0.5, # comp ratio
        100, # token before
        50, # token after
        10, # items before
        5 # items after
    ))

    engine._build_window = MagicMock(return_value=(
            ContextWindow(
                sections=[],
                token_estimate=50,
                budget=0
            ),
        15.0 # win latency
    ))

    return engine

@pytest.mark.asyncio
async def test_context_engine_build_success(engine, ctx, command):
    result = await engine.build(ctx, command)

    assert result.context_id is not None
    assert result.metadata.policy_id == "planning"
    assert result.metadata.successful_providers == 1
    assert result.window.token_estimate == 50

    engine._execute_providers.assert_called_once()
    engine._validate.assert_called_once()
    engine._rank.assert_called_once()
    engine._compress.assert_called_once()
    engine._build_window.assert_called_once()

@pytest.mark.asyncio
async def test_context_engine_build_unknown_policy(engine, ctx, command):
    command.policy_id = "unknown_policy"
    with pytest.raises(ContextAssemblyError):
        await engine.build(ctx, command)

@pytest.mark.asyncio
async def test_context_engine_build_required_provider_failure(engine, ctx, command):
    # Mock a required provider failing
    engine._execute_providers.return_value = ([], [
        ProviderFailureRecord(
            provider=ContextSource.TWIN,
            error_type="TIMEOUT",
            error_message="Timeout",
            latency_ms=500.0,
            stack_trace=""
        )
    ], {"TWIN_MEMORY": 500.0})

    # We need to mock a policy that requires TWIN_MEMORY
    from app.application.context.foundation.context_policies import ContextPolicy
    class MockPolicy(ContextPolicy):
        policy_id: str = "planning"
        enabled_providers: set[ContextSource] = {ContextSource.TWIN}
        required_providers: set[ContextSource] = {ContextSource.TWIN}
        strict_validation: bool = True

    import app.application.context.engine as engine_module
    original_policies = engine_module.BUILT_IN_POLICIES
    engine_module.BUILT_IN_POLICIES = {"planning": MockPolicy()}

    try:
        with pytest.raises(ContextAssemblyError):
            await engine.build(ctx, command)
    finally:
        engine_module.BUILT_IN_POLICIES = original_policies
