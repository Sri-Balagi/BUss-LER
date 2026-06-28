import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.context_engine import (
    ContextEngine,
    ContextAssemblyError,
    ContextValidationError,
)
from app.models.enterprise_context import (
    EnterpriseContextCreate,
    ExecutionPlan,
    ContextSection,
    ContextWindow,
)
from app.models.enums import ContextSource, ContextStatus
from app.core.context import OperationContext


@pytest.fixture
def mock_registry():
    return MagicMock()


@pytest.fixture
def mock_graph():
    return MagicMock()


@pytest.fixture
def mock_validator():
    return MagicMock()


@pytest.fixture
def mock_ranker():
    return MagicMock()


@pytest.fixture
def mock_compressor():
    return MagicMock()


@pytest.fixture
def mock_window_builder():
    return MagicMock()


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def mock_event_bus():
    return MagicMock()


@pytest.fixture
def mock_trace_service():
    return AsyncMock()


@pytest.fixture
def engine(
    mock_registry,
    mock_graph,
    mock_validator,
    mock_ranker,
    mock_compressor,
    mock_window_builder,
    mock_repository,
    mock_event_bus,
    mock_trace_service,
):
    return ContextEngine(
        provider_registry=mock_registry,
        dependency_graph=mock_graph,
        validator=mock_validator,
        ranker=mock_ranker,
        compressor=mock_compressor,
        window_builder=mock_window_builder,
        repository=mock_repository,
        event_bus=mock_event_bus,
        trace_service=mock_trace_service,
    )


@pytest.mark.asyncio
async def test_build_success(
    engine,
    mock_graph,
    mock_registry,
    mock_validator,
    mock_ranker,
    mock_compressor,
    mock_window_builder,
):
    ctx = OperationContext(
        request_id="req1", correlation_id="cor1", user_id=uuid.uuid4()
    )
    command = EnterpriseContextCreate(twin_id=uuid.uuid4(), policy_id="full")

    mock_graph.resolve.return_value = ExecutionPlan(
        batches=[[ContextSource.MEMORY]], total_providers=1
    )

    mock_provider_entry = MagicMock()
    mock_provider = AsyncMock()

    from app.models.enterprise_context import ContextItem, ContextProvenance

    prov = ContextProvenance(provider=ContextSource.MEMORY, service_name="test")
    item = ContextItem(source=ContextSource.MEMORY, content="test", provenance=prov)
    section = ContextSection(source=ContextSource.MEMORY, items=[item])

    mock_provider.provide.return_value = section
    mock_provider_entry.provider = mock_provider

    from app.services.context_retry import ProviderRetryConfig

    mock_provider_entry.retry_config = ProviderRetryConfig(
        max_retries=1, base_delay_ms=10
    )
    mock_registry.get_entry.return_value = mock_provider_entry

    validation_result = MagicMock()
    validation_result.is_valid = True
    mock_validator.validate.return_value = validation_result

    mock_ranker.rank.return_value = [section]
    mock_compressor.compress.return_value = [section]

    window = ContextWindow(
        budget=1000, sections=[section], window_id=uuid.uuid4(), metadata={}
    )
    mock_window_builder.build_window.return_value = window

    result = await engine.build(ctx, command)

    assert result.status == ContextStatus.OPTIMIZED
    assert len(result.sections) == 1
    assert result.sections[0].source == ContextSource.MEMORY


@pytest.mark.asyncio
async def test_build_unknown_policy(engine):
    ctx = OperationContext(
        request_id="req1", correlation_id="cor1", user_id=uuid.uuid4()
    )
    command = EnterpriseContextCreate(twin_id=uuid.uuid4(), policy_id="invalid_policy")
    with pytest.raises(ContextAssemblyError):
        await engine.build(ctx, command)


@pytest.mark.asyncio
async def test_build_required_provider_failure(engine, mock_graph, mock_registry):
    ctx = OperationContext(
        request_id="req1", correlation_id="cor1", user_id=uuid.uuid4()
    )
    command = EnterpriseContextCreate(twin_id=uuid.uuid4(), policy_id="planning")

    mock_graph.resolve.return_value = ExecutionPlan(
        batches=[[ContextSource.GOAL]], total_providers=1
    )

    mock_provider_entry = MagicMock()
    mock_provider = MagicMock()
    mock_provider.provide = AsyncMock(side_effect=Exception("Provider crash"))
    mock_provider_entry.provider = mock_provider
    from app.services.context_retry import ProviderRetryConfig

    mock_provider_entry.retry_config = ProviderRetryConfig(
        max_retries=1, base_delay_ms=10
    )
    mock_registry.get_entry.return_value = mock_provider_entry

    with pytest.raises(ContextAssemblyError) as exc_info:
        await engine.build(ctx, command)
    assert "Required providers failed" in exc_info.value.detail


@pytest.mark.asyncio
async def test_build_validation_failure(
    engine, mock_graph, mock_registry, mock_validator
):
    ctx = OperationContext(
        request_id="req1", correlation_id="cor1", user_id=uuid.uuid4()
    )
    command = EnterpriseContextCreate(twin_id=uuid.uuid4(), policy_id="full")

    mock_graph.resolve.return_value = ExecutionPlan(
        batches=[[ContextSource.MEMORY]], total_providers=1
    )

    mock_provider_entry = MagicMock()
    mock_provider = AsyncMock()
    from app.models.enterprise_context import ContextItem, ContextProvenance

    prov = ContextProvenance(provider=ContextSource.MEMORY, service_name="test")
    item = ContextItem(source=ContextSource.MEMORY, content="test", provenance=prov)
    section = ContextSection(source=ContextSource.MEMORY, items=[item])
    mock_provider.provide.return_value = section
    mock_provider_entry.provider = mock_provider
    from app.services.context_retry import ProviderRetryConfig

    mock_provider_entry.retry_config = ProviderRetryConfig(
        max_retries=1, base_delay_ms=10
    )
    mock_registry.get_entry.return_value = mock_provider_entry

    validation_result = MagicMock()
    validation_result.is_valid = False
    validation_result.errors = ["Invalid context data"]
    mock_validator.validate.return_value = validation_result

    with pytest.raises(ContextValidationError):
        await engine.build(ctx, command)
