from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.infrastructure.ai.budgets.interfaces import IResourceBudget, ResourceBudgetType
from app.infrastructure.ai.budgets.models import TokenBudget
from app.infrastructure.ai.kernel import AIKernel
from app.infrastructure.ai.models import (
    AIRequest,
    AIRequestLifecycle,
    BudgetExceededError,
    ClassifyRequest,
    EmbeddingRequest,
    StructuredRequest,
)
from app.infrastructure.ai.prompts import PromptManager, PromptTemplate
from app.infrastructure.ai.providers.mock.provider import MockLLMProvider
from app.infrastructure.ai.router import ProviderRouter


class MockBudgetService(IResourceBudget):
    def __init__(self):
        self.pre_check_mock = AsyncMock()
        self.record_consumption_mock = AsyncMock()
        self.get_status_mock = AsyncMock()

    @property
    def budget_type(self) -> ResourceBudgetType:
        return ResourceBudgetType.TOKEN

    async def pre_check(self, entity_id: str, estimated_cost: int = 0) -> None:
        await self.pre_check_mock(entity_id, estimated_cost)

    async def record_consumption(
        self,
        entity_id: str,
        lifecycle_id: str,
        amount: int,
        session_id: str | None = None,
        **kwargs,
    ) -> None:
        await self.record_consumption_mock(
            entity_id=entity_id,
            lifecycle_id=lifecycle_id,
            amount=amount,
            session_id=session_id,
            **kwargs,
        )

    async def get_status(self, entity_id: str) -> TokenBudget:
        return await self.get_status_mock(entity_id)


@pytest.fixture
def mock_provider():
    return MockLLMProvider()


@pytest.fixture
def router(mock_provider):
    router_mock = MagicMock(spec=ProviderRouter)
    router_mock.get_active_provider.return_value = mock_provider
    router_mock.get_provider_for_capability.return_value = mock_provider

    async def mock_route_with_fallback(primary, operation, *args, **kwargs):
        return await operation(primary, *args, **kwargs)

    router_mock.route_with_fallback = AsyncMock(side_effect=mock_route_with_fallback)

    # Setup registry mock for health checks
    registry_mock = MagicMock()
    registry_mock.list_providers.return_value = [mock_provider]
    router_mock._registry = registry_mock

    return router_mock


@pytest.fixture
def prompt_manager():
    manager_mock = MagicMock(spec=PromptManager)
    manager_mock.resolve.return_value = "resolved user prompt"
    return manager_mock


@pytest.fixture
def budget_service():
    return MockBudgetService()


@pytest.fixture
def ai_kernel(router, prompt_manager, budget_service):
    return AIKernel(router=router, prompt_manager=prompt_manager, budget=budget_service)


@pytest.mark.asyncio
async def test_generate_service_invocation_and_lifecycle(
    ai_kernel, router, prompt_manager, budget_service, mock_provider
):
    """
    Verify:
    - Service Invocation Verification: PromptRegistry, IResourceBudget, ProviderRouter, Provider, Budget Record
    - Lifecycle Propagation: lifecycle identifier is propagated identical through the stack.
    """
    request = AIRequest(prompt_id="test_prompt", version="v1")

    # Override provider's generate to capture the lifecycle from request
    original_generate = mock_provider.generate
    captured_request = None

    async def mock_generate(req, resolved):
        nonlocal captured_request
        captured_request = req
        return await original_generate(req, resolved)

    mock_provider.generate = AsyncMock(side_effect=mock_generate)

    response = await ai_kernel.generate(request)

    # Verify PromptRegistry
    prompt_manager.resolve.assert_called_once_with("test_prompt", "v1", {})

    # Verify pre_check
    budget_service.pre_check_mock.assert_called_once_with("system", 0)

    # Verify router
    router.get_active_provider.assert_called_once_with(None)

    # Verify Provider execution
    mock_provider.generate.assert_called_once()

    # Verify Lifecycle Propagation
    assert captured_request.lifecycle is not None
    assert isinstance(captured_request.lifecycle, AIRequestLifecycle)
    assert captured_request.lifecycle.operation == "generate"

    # Verify Budget record_consumption
    budget_service.record_consumption_mock.assert_called_once()
    call_args = budget_service.record_consumption_mock.call_args[1]
    assert call_args["lifecycle_id"] == captured_request.lifecycle.lifecycle_id


@pytest.mark.asyncio
async def test_generate_budget_hard_stop(
    ai_kernel, router, prompt_manager, budget_service, mock_provider
):
    """
    Verify that BudgetExceededError stops execution before routing occurs.
    - ProviderRouter is never called.
    - Provider execution never occurs.
    - Budget consumption is never recorded.
    """
    request = AIRequest(prompt_id="test_prompt")

    budget_service.pre_check_mock.side_effect = BudgetExceededError(
        entity_id="system", policy="HARD_STOP", detail="test"
    )

    mock_provider.generate = AsyncMock()

    with pytest.raises(BudgetExceededError):
        await ai_kernel.generate(request)

    prompt_manager.resolve.assert_called_once()
    router.get_active_provider.assert_not_called()
    mock_provider.generate.assert_not_called()
    budget_service.record_consumption_mock.assert_not_called()


@pytest.mark.asyncio
async def test_generate_structured(
    ai_kernel, router, prompt_manager, mock_provider, budget_service
):
    from pydantic import BaseModel

    class Dummy(BaseModel):
        field: str

    req = AIRequest(prompt_id="test")
    mock_provider.generate_structured = AsyncMock()

    # create a mock response matching Pydantic expectations
    mock_resp = Dummy(field="value")
    mock_provider.generate_structured.return_value = mock_resp

    await ai_kernel.generate_structured(req, response_schema=Dummy)

    router.get_provider_for_capability.assert_called_once_with(
        required_capability="supports_structured_output", preferred_provider=None
    )
    mock_provider.generate_structured.assert_called_once()
    budget_service.record_consumption_mock.assert_called_once()


@pytest.mark.asyncio
async def test_embed(ai_kernel, router, mock_provider, budget_service):
    req = EmbeddingRequest(text="test")
    mock_provider.embed = AsyncMock()

    mock_resp = MagicMock()
    mock_resp.vector = [0.1, 0.2, 0.3]
    mock_resp.metadata.model = "mock"
    mock_resp.metadata.latency_ms = 50
    mock_provider.embed.return_value = mock_resp

    await ai_kernel.embed(req)

    router.get_provider_for_capability.assert_called_once_with(
        required_capability="supports_embeddings", preferred_provider=None
    )
    budget_service.pre_check_mock.assert_called_once()
    mock_provider.embed.assert_called_once()
    budget_service.record_consumption_mock.assert_called_once()

    call_args = budget_service.record_consumption_mock.call_args[1]
    assert call_args["amount"] == 3


@pytest.mark.asyncio
async def test_health_check(ai_kernel, mock_provider):
    mock_provider.health_check = AsyncMock(return_value={"status": "healthy"})

    result = await ai_kernel.health_check()
    assert result["status"] == "ok"
    assert "mock" in result["providers"]
    assert result["providers"]["mock"]["status"] == "healthy"
