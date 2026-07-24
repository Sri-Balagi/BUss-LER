from datetime import UTC, datetime, timezone
from uuid import UUID

import pytest

from app.domain.common.biz_object import BizObject


def test_biz_object_defaults():
    obj = BizObject()
    assert isinstance(obj.id, UUID)
    assert obj.version == 1
    assert obj.tenant_id is None
    assert obj.owner_id is None
    assert obj.correlation_id is None
    assert obj.metadata == {}
    assert obj.tags == []
    assert isinstance(obj.created_at, datetime)
    assert isinstance(obj.updated_at, datetime)

def test_biz_object_update():
    obj = BizObject()
    old_version = obj.version
    old_updated = obj.updated_at

    # Wait a tiny bit to ensure timestamp changes if resolution allows
    # In practice, version bump is enough to test mutation

    obj.update(metadata={"key": "value"}, tags=["test"])

    assert obj.version == old_version + 1
    assert obj.updated_at >= old_updated
    assert obj.metadata == {"key": "value"}
    assert obj.tags == ["test"]

def test_biz_object_cannot_update_id_or_created_at():
    obj = BizObject()
    old_id = obj.id
    old_created_at = obj.created_at

    obj.update(id="new-id", created_at=datetime.now(UTC))

    assert obj.id == old_id
    assert obj.created_at == old_created_at
