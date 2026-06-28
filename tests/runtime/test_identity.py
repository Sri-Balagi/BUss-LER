from uuid import uuid4
from app.runtime.session.runtime_identity import RuntimeIdentity

def test_runtime_identity_generation():
    identity = RuntimeIdentity()
    assert identity.session_id is not None
    assert identity.execution_id is not None
    assert identity.correlation_id is not None
    assert identity.parent_execution_id is None
    assert identity.created_at is not None

def test_runtime_identity_with_parent():
    parent_id = uuid4()
    identity = RuntimeIdentity(parent_execution_id=parent_id)
    assert identity.parent_execution_id == parent_id
