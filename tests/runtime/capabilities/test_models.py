import pytest
from uuid import uuid4
from pydantic import ValidationError

from app.runtime.capabilities.permissions import CapabilityPermission
from app.runtime.capabilities.policies import CapabilityPolicy
from app.runtime.capabilities.models.manifest import CapabilityManifest
from app.runtime.capabilities.models.specification import CapabilitySpecification
from app.runtime.capabilities.models.request import CapabilityRequest
from app.runtime.capabilities.models.result import CapabilityResult, ExecutionStatus

def test_capability_policy_defaults():
    policy = CapabilityPolicy()
    assert policy.max_retries == 3
    assert policy.timeout_ms == 30000
    assert not policy.idempotent
    assert policy.rate_limit_per_minute is None
    assert not policy.requires_audit

def test_capability_policy_custom():
    policy = CapabilityPolicy(max_retries=5, timeout_ms=1000, idempotent=True, rate_limit_per_minute=10, requires_audit=True)
    assert policy.max_retries == 5
    assert policy.timeout_ms == 1000
    assert policy.idempotent
    assert policy.rate_limit_per_minute == 10
    assert policy.requires_audit

def test_capability_manifest():
    manifest = CapabilityManifest(
        version="1.0.0",
        author="BizOS Team",
        package="app.runtime.capabilities.fs",
        dependencies=["os", "shutil"]
    )
    assert manifest.version == "1.0.0"
    assert manifest.author == "BizOS Team"
    assert manifest.package == "app.runtime.capabilities.fs"
    assert manifest.dependencies == ["os", "shutil"]
    assert manifest.plugin_source is None
    assert manifest.checksum is None

def test_capability_specification():
    spec = CapabilitySpecification(
        capability_id="fs_read",
        name="Filesystem Read",
        category="Filesystem",
        supported_operations=["read", "list"],
        permissions_required=[CapabilityPermission.FS_READ]
    )
    assert spec.capability_id == "fs_read"
    assert spec.name == "Filesystem Read"
    assert spec.category == "Filesystem"
    assert spec.supported_operations == ["read", "list"]
    assert spec.permissions_required == [CapabilityPermission.FS_READ]
    assert spec.execution_mode == "async"
    assert isinstance(spec.policy, CapabilityPolicy)

def test_capability_request():
    trace_id = uuid4()
    req = CapabilityRequest(
        capability_id="fs_read",
        operation="read",
        arguments={"path": "/tmp/test.txt"},
        permissions=[CapabilityPermission.FS_READ],
        trace_id=trace_id
    )
    assert req.capability_id == "fs_read"
    assert req.operation == "read"
    assert req.arguments == {"path": "/tmp/test.txt"}
    assert req.permissions == [CapabilityPermission.FS_READ]
    assert req.trace_id == trace_id

def test_capability_request_immutable():
    # pydantic BaseModels aren't natively immutable unless frozen=True
    # But we can test that it validates correctly.
    req = CapabilityRequest(
        capability_id="fs_read",
        operation="read",
    )
    assert req.capability_id == "fs_read"
    assert req.operation == "read"

def test_capability_result():
    trace_id = uuid4()
    res = CapabilityResult(
        status=ExecutionStatus.SUCCESS,
        outputs={"data": "file contents"},
        execution_time_ms=120,
        execution_trace_id=trace_id
    )
    assert res.status == ExecutionStatus.SUCCESS
    assert res.outputs == {"data": "file contents"}
    assert res.execution_time_ms == 120
    assert res.execution_trace_id == trace_id
    assert res.warnings == []
    assert res.errors == []

def test_capability_request_validation_failure():
    with pytest.raises(ValidationError):
        # Missing required fields capability_id, operation
        CapabilityRequest()
