import pytest
from uuid import uuid4

from app.runtime.capabilities.models.specification import CapabilitySpecification
from app.runtime.capabilities.models.request import CapabilityRequest
from app.runtime.capabilities.models.result import ExecutionStatus
from app.runtime.capabilities.permissions import CapabilityPermission
from app.runtime.capabilities.context import CapabilityContext
from app.runtime.capabilities.factories import TransientCapabilityFactory, SingletonCapabilityFactory
from app.runtime.capabilities.lifecycle import CapabilityLifecycleManager

from tests.runtime.capabilities.mocks.adapters import (
    MockFilesystemAdapter,
    MockDatabaseAdapter,
    MockNetworkAdapter
)
from tests.runtime.capabilities.mocks.capabilities import (
    ReadFileCapability,
    HttpGetCapability,
    QueryDatabaseCapability
)

@pytest.fixture
def fs_spec():
    return CapabilitySpecification(
        capability_id="fs_read",
        name="Filesystem Read",
        category="Filesystem",
        supported_operations=["read"],
        permissions_required=[CapabilityPermission.FS_READ]
    )

@pytest.fixture
def db_spec():
    return CapabilitySpecification(
        capability_id="db_query",
        name="Database Query",
        category="Database",
        supported_operations=["query"],
        permissions_required=[CapabilityPermission.DB_READ]
    )
    
@pytest.fixture
def net_spec():
    return CapabilitySpecification(
        capability_id="net_get",
        name="Network GET",
        category="Network",
        supported_operations=["get", "fail"],
        permissions_required=[CapabilityPermission.NETWORK_HTTP_GET]
    )

@pytest.mark.anyio
async def test_adapter_initialization_and_cleanup(fs_spec):
    adapter = MockFilesystemAdapter()
    assert not adapter.initialized
    assert not adapter.connected
    
    await adapter.initialize()
    assert adapter.initialized
    
    await adapter.connect()
    assert adapter.connected
    
    await adapter.disconnect()
    assert not adapter.connected
    
    await adapter.cleanup()
    assert not adapter.initialized

@pytest.mark.anyio
async def test_transient_factory(fs_spec):
    factory = TransientCapabilityFactory(ReadFileCapability, MockFilesystemAdapter)
    cap1 = factory.create(fs_spec)
    cap2 = factory.create(fs_spec)
    
    assert isinstance(cap1, ReadFileCapability)
    assert isinstance(cap2, ReadFileCapability)
    assert cap1 is not cap2
    assert cap1.adapter is not cap2.adapter

@pytest.mark.anyio
async def test_singleton_factory(fs_spec):
    factory = SingletonCapabilityFactory(ReadFileCapability, MockFilesystemAdapter)
    cap1 = factory.create(fs_spec)
    cap2 = factory.create(fs_spec)
    
    assert cap1 is cap2
    assert cap1.adapter is cap2.adapter

@pytest.mark.anyio
async def test_capability_lifecycle_success(fs_spec):
    factory = TransientCapabilityFactory(ReadFileCapability, MockFilesystemAdapter)
    cap = factory.create(fs_spec)
    manager = CapabilityLifecycleManager(cap)
    context = CapabilityContext()
    
    req = CapabilityRequest(
        capability_id="fs_read",
        operation="read",
        arguments={"path": "/tmp/test.txt"},
        permissions=[CapabilityPermission.FS_READ],
        trace_id=uuid4()
    )
    
    res = await manager.execute_request(req, context)
    
    assert res.status == ExecutionStatus.SUCCESS
    assert res.outputs == {"data": "file_contents_mock"}
    assert res.execution_trace_id == req.trace_id
    assert cap.adapter.initialized == False  # Because cleanup was called
    assert cap.adapter.connected == False

@pytest.mark.anyio
async def test_capability_lifecycle_validation_failure(fs_spec):
    factory = TransientCapabilityFactory(ReadFileCapability, MockFilesystemAdapter)
    cap = factory.create(fs_spec)
    manager = CapabilityLifecycleManager(cap)
    context = CapabilityContext()
    
    req = CapabilityRequest(
        capability_id="fs_read",
        operation="write",  # Not supported
        arguments={"path": "/tmp/test.txt"},
        permissions=[CapabilityPermission.FS_WRITE]
    )
    
    res = await manager.execute_request(req, context)
    
    assert res.status == ExecutionStatus.FAILURE
    assert len(res.errors) == 1
    assert "not supported" in res.errors[0]
    
    # Ensure cleanup still ran
    assert cap.adapter.initialized == False
    assert cap.adapter.connected == False

@pytest.mark.anyio
async def test_capability_lifecycle_execution_failure(net_spec):
    factory = TransientCapabilityFactory(HttpGetCapability, MockNetworkAdapter)
    cap = factory.create(net_spec)
    manager = CapabilityLifecycleManager(cap)
    context = CapabilityContext()
    
    req = CapabilityRequest(
        capability_id="net_get",
        operation="fail",
        arguments={"url": "http://example.com"},
        permissions=[CapabilityPermission.NETWORK_HTTP_GET]
    )
    
    res = await manager.execute_request(req, context)
    
    assert res.status == ExecutionStatus.FAILURE
    assert len(res.errors) == 1
    assert "Mock network failure" in res.errors[0]
    
    # Ensure cleanup still ran
    assert cap.adapter.initialized == False
    assert cap.adapter.connected == False

@pytest.mark.anyio
async def test_integration_database_query(db_spec):
    factory = SingletonCapabilityFactory(QueryDatabaseCapability, MockDatabaseAdapter)
    cap = factory.create(db_spec)
    manager = CapabilityLifecycleManager(cap)
    context = CapabilityContext()
    
    req = CapabilityRequest(
        capability_id="db_query",
        operation="query",
        arguments={"sql": "SELECT 1"},
        permissions=[CapabilityPermission.DB_READ]
    )
    
    res1 = await manager.execute_request(req, context)
    assert res1.status == ExecutionStatus.SUCCESS
    
    res2 = await manager.execute_request(req, context)
    assert res2.status == ExecutionStatus.SUCCESS
    
    assert cap.adapter.query_count == 2
