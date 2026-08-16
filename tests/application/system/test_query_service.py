from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.system.query_service import SystemQueryService


@pytest.fixture
def mock_runtime_manager():
    return MagicMock()

@pytest.fixture
def mock_tool_registry():
    return AsyncMock()

@pytest.fixture
def mock_workflow_registry():
    return AsyncMock()

@pytest.fixture
def query_service(mock_runtime_manager, mock_tool_registry, mock_workflow_registry):
    return SystemQueryService(
        runtime_manager=mock_runtime_manager,
        tool_registry=mock_tool_registry,
        workflow_registry=mock_workflow_registry
    )

@pytest.mark.asyncio
async def test_list_active_workflows_empty(query_service):
    # Base case, runtime manager doesn't have process_manager
    workflows = await query_service.list_active_workflows()
    assert workflows == []

@pytest.mark.asyncio
async def test_list_active_workflows_with_manager(query_service):
    process = MagicMock()
    process.pid = 123
    process.state.name = "RUNNING"
    process.start_time.isoformat.return_value = "2024-01-01T00:00:00Z"

    process_manager = MagicMock()
    process_manager.list_processes.return_value = [process]

    query_service.runtime_manager.process_manager = process_manager

    workflows = await query_service.list_active_workflows()
    assert len(workflows) == 1
    assert workflows[0] == {
        "id": "123",
        "status": "RUNNING",
        "started": "2024-01-01T00:00:00Z"
    }

@pytest.mark.asyncio
async def test_list_registry_items_invalid_registry(query_service):
    with pytest.raises(ValueError, match="Registry not found: InvalidRegistry"):
        await query_service.list_registry_items("InvalidRegistry")

@pytest.mark.asyncio
async def test_list_registry_items_with_pydantic(query_service, mock_tool_registry):
    class MockPydantic:
        def model_dump(self):
            return {"name": "tool1"}

    mock_tool_registry.list_all.return_value = [MockPydantic()]

    items = await query_service.list_registry_items("ToolRegistry")
    assert items == [{"name": "tool1"}]

@pytest.mark.asyncio
async def test_list_registry_items_with_to_dict(query_service, mock_tool_registry):
    class MockToDict:
        def to_dict(self):
            return {"name": "tool2"}

    mock_tool_registry.list_all.return_value = [MockToDict()]

    items = await query_service.list_registry_items("ToolRegistry")
    assert items == [{"name": "tool2"}]

@pytest.mark.asyncio
async def test_list_registry_items_with_basic_fallback(query_service, mock_tool_registry):
    class MockBasic:
        id = "1"
        name = "tool3"
        type = "basic"

    mock_tool_registry.list_all.return_value = [MockBasic()]

    items = await query_service.list_registry_items("ToolRegistry")
    assert items == [{"id": "1", "name": "tool3", "type": "basic"}]

@pytest.mark.asyncio
async def test_get_memory_status(query_service):
    status = await query_service.get_memory_status()
    assert status["status"] == "Not Yet Available"
