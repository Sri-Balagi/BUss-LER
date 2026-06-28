import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.core.context import OperationContext
from app.models.enterprise_context import (
    ContextSection,
    ContextWindow,
    ContextItem,
    EnterpriseContextCreate,
)
from app.models.enums import ContextSource, ContextStatus
from app.services.context_engine import ContextEngine
from app.services.context_retry import ProviderRetryConfig
from app.services.context_policies import BUILT_IN_POLICIES

@pytest.mark.asyncio
async def test_context_engine_build_success():
    # Setup mocks
    mock_registry = MagicMock()
    mock_graph = MagicMock()
    mock_validator = MagicMock()
    mock_ranker = MagicMock()
    mock_compressor = MagicMock()
    mock_window_builder = MagicMock()
    mock_repository = AsyncMock()
    
    mock_provider = MagicMock()
    mock_provider.provide = AsyncMock()
    mock_item = ContextItem.model_construct(item_id=uuid4(), source=ContextSource.MEMORY, content="test", token_estimate=10)
    mock_section = ContextSection(source=ContextSource.MEMORY, items=[mock_item])
    mock_provider.provide.return_value = mock_section
    mock_entry = MagicMock()
    mock_entry.provider = mock_provider
    mock_entry.retry_config = ProviderRetryConfig(max_retries=1, backoff_base=0.1, max_delay=1.0, jitter=False, timeout_seconds=5.0)
    mock_registry.get_entry.return_value = mock_entry
    
    # Mock Graph
    mock_execution_plan = MagicMock()
    mock_execution_plan.batches = [[ContextSource.MEMORY]]
    mock_execution_plan.total_providers = 1
    mock_graph.resolve.return_value = mock_execution_plan
    
    # Mock Validator
    mock_validation_result = MagicMock()
    mock_validation_result.is_valid = True
    mock_validator.validate.return_value = mock_validation_result
    
    # Mock Strategies
    mock_ranker.rank.return_value = [mock_section]
    mock_compressor.compress.return_value = [mock_section]
    mock_window = ContextWindow(sections=[mock_section], token_estimate=10, budget=100, items_included=0, items_excluded=0, overflow=False)
    mock_window_builder.build_window.return_value = mock_window
    
    engine = ContextEngine(
        provider_registry=mock_registry,
        dependency_graph=mock_graph,
        validator=mock_validator,
        ranker=mock_ranker,
        compressor=mock_compressor,
        window_builder=mock_window_builder,
        repository=mock_repository,
    )
    
    command = EnterpriseContextCreate(
        twin_id=uuid4(),
        policy_id="planning"
    )
    ctx = MagicMock(spec=OperationContext)
    ctx.request_id = "test_request"
    ctx.bind_to_logger.return_value = MagicMock()
    
    # Execute
    enterprise_context = await engine.build(ctx, command)
    
    # Assertions
    assert enterprise_context is not None
    assert enterprise_context.window == mock_window
    assert enterprise_context.metadata.successful_providers == 1
    assert enterprise_context.metadata.failed_providers == 0
    
    # Verify repository calls
    assert mock_repository.create.called
    assert mock_repository.update_status.called

@pytest.mark.asyncio
async def test_context_engine_unknown_policy():
    engine = ContextEngine(
        provider_registry=MagicMock(),
        dependency_graph=MagicMock(),
        validator=MagicMock(),
        ranker=MagicMock(),
        compressor=MagicMock(),
        window_builder=MagicMock(),
    )
    
    command = EnterpriseContextCreate(
        twin_id=uuid4(),
        policy_id="unknown_policy_123"
    )
    
    with pytest.raises(Exception) as excinfo:
        await engine.build(MagicMock(), command)
    assert "Unknown context policy" in getattr(excinfo.value, "detail", str(excinfo.value))

@pytest.mark.asyncio
async def test_context_engine_validation_failure():
    # Setup mocks
    mock_registry = MagicMock()
    mock_graph = MagicMock()
    mock_validator = MagicMock()
    
    mock_provider = AsyncMock()
    mock_entry = MagicMock()
    mock_entry.provider = mock_provider
    mock_entry.retry_config = ProviderRetryConfig(max_retries=1, backoff_base=0.1, max_delay=1.0, jitter=False, timeout_seconds=5.0)
    mock_registry.get_entry.return_value = mock_entry
    
    mock_execution_plan = MagicMock()
    mock_execution_plan.batches = [[ContextSource.MEMORY]]
    mock_execution_plan.total_providers = 1
    mock_graph.resolve.return_value = mock_execution_plan
    
    mock_validation_result = MagicMock()
    mock_validation_result.is_valid = False
    mock_validation_result.errors = ["Validation failed!"]
    mock_validator.validate.return_value = mock_validation_result
    
    engine = ContextEngine(
        provider_registry=mock_registry,
        dependency_graph=mock_graph,
        validator=mock_validator,
        ranker=MagicMock(),
        compressor=MagicMock(),
        window_builder=MagicMock(),
    )
    
    command = EnterpriseContextCreate(
        twin_id=uuid4(),
        policy_id="planning"
    )
    ctx = MagicMock(spec=OperationContext)
    ctx.request_id = "test_request"
    ctx.bind_to_logger.return_value = MagicMock()
    
    with pytest.raises(Exception) as excinfo:
        await engine.build(ctx, command)
    assert "Validation failed!" in getattr(excinfo.value, "detail", str(excinfo.value))
