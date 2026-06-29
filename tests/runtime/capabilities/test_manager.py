import pytest
from uuid import uuid4
from app.runtime.capabilities.manager import CapabilityManager
from app.runtime.capabilities.registry import CapabilityRegistry
from app.runtime.capabilities.factories import TransientCapabilityFactory
from app.runtime.capabilities.models.specification import CapabilitySpecification
from app.runtime.capabilities.models.request import CapabilityRequest
from app.runtime.capabilities.models.result import ExecutionStatus
from app.runtime.capabilities.middleware.logging import LoggingMiddleware
from tests.runtime.capabilities.mocks.capabilities import ReadFileCapability
from tests.runtime.capabilities.mocks.adapters import MockFilesystemAdapter

@pytest.fixture
def spec():
    return CapabilitySpecification(
        capability_id="fs_read",
        name="FS Read",
        category="FS",
        supported_operations=["read"],
        version="1.0.0"
    )

@pytest.fixture
def manager(spec):
    registry = CapabilityRegistry()
    registry.register(spec, TransientCapabilityFactory(ReadFileCapability, MockFilesystemAdapter))
    return CapabilityManager(registry, middlewares=[LoggingMiddleware()])

@pytest.mark.anyio
async def test_capability_manager_execution(manager):
    req = CapabilityRequest(
        capability_id="fs_read",
        operation="read",
        arguments={"path": "/mock"},
        trace_id=uuid4()
    )
    
    res = await manager.execute_capability(req)
    
    assert res.status == ExecutionStatus.SUCCESS
    assert res.outputs == {"data": "file_contents_mock"}
    assert res.execution_trace_id == req.trace_id

@pytest.mark.anyio
async def test_capability_manager_resolution_failure(manager):
    req = CapabilityRequest(
        capability_id="missing",
        operation="read",
        arguments={}
    )
    
    res = await manager.execute_capability(req)
    
    assert res.status == ExecutionStatus.FAILURE
    assert "Resolution failure" in res.errors[0]
