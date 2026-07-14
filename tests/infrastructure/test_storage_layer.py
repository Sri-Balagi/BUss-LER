"""
Wave-2 Milestone 4: Storage Layer — Unit Tests
===============================================
Tests for PostgresMount, QdrantMount, RedisMount, SnapshotManager,
BackupManager, and ConcreteStorageManager.

All external clients (Supabase, Qdrant, Redis) are mocked.
No live infrastructure is required.
"""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch
from uuid import uuid4, UUID

import pytest

# ---------------------------------------------------------------------------
# PostgresMount
# ---------------------------------------------------------------------------

from app.infrastructure.vfs.postgres_mount import PostgresMount, PostgresNode


def test_postgres_mount_scheme():
    mount = PostgresMount(supabase_client=None)
    assert mount.scheme == "pg"


def test_postgres_mount_resolve_returns_node():
    mount = PostgresMount(supabase_client=None)
    uri = "pg://digital_twins/abc-123"
    node = mount.resolve(uri)
    assert isinstance(node, PostgresNode)
    assert node.path == uri
    assert node.metadata["scheme"] == "pg"


def test_postgres_node_read_without_client():
    mount = PostgresMount(supabase_client=None)
    node = mount.resolve("pg://digital_twins/abc-123")
    result = node.read()
    # Without a client, read() returns a structured placeholder
    assert "note" in result
    assert result["table"] == "digital_twins"
    assert result["row_id"] == "abc-123"


# ---------------------------------------------------------------------------
# QdrantMount
# ---------------------------------------------------------------------------

from app.infrastructure.vfs.qdrant_mount import QdrantMount, QdrantNode


def test_qdrant_mount_scheme():
    mount = QdrantMount(qdrant_client=None)
    assert mount.scheme == "qdrant"


def test_qdrant_mount_resolve_returns_node():
    mount = QdrantMount(qdrant_client=None)
    uri = "qdrant://memories/vector-456"
    node = mount.resolve(uri)
    assert isinstance(node, QdrantNode)
    assert node.path == uri
    assert node.metadata["scheme"] == "qdrant"


def test_qdrant_node_read_without_client():
    mount = QdrantMount(qdrant_client=None)
    node = mount.resolve("qdrant://memories/vector-456")
    result = node.read()
    assert "note" in result
    assert result["collection"] == "memories"
    assert result["point_id"] == "vector-456"


# ---------------------------------------------------------------------------
# RedisMount
# ---------------------------------------------------------------------------

from app.infrastructure.vfs.redis_mount import RedisMount, RedisNode


def test_redis_mount_scheme():
    mock_client = MagicMock()
    mount = RedisMount(redis_client=mock_client)
    assert mount.scheme == "redis"


def test_redis_mount_resolve_returns_node():
    mock_client = MagicMock()
    mount = RedisMount(redis_client=mock_client)
    uri = "redis://session:user-xyz"
    node = mount.resolve(uri)
    assert isinstance(node, RedisNode)
    assert node.path == uri


def test_redis_node_read_returns_deserialized_value():
    mock_client = MagicMock()
    mock_client.get.return_value = json.dumps({"key": "value"})
    mount = RedisMount(redis_client=mock_client)
    node = mount.resolve("redis://session:user-xyz")
    result = node.read()
    assert result == {"key": "value"}
    mock_client.get.assert_called_once_with("session:user-xyz")


def test_redis_node_write_stores_json():
    mock_client = MagicMock()
    mount = RedisMount(redis_client=mock_client)
    node = mount.resolve("redis://session:user-xyz")
    node.write({"status": "active"})
    mock_client.set.assert_called_once_with("session:user-xyz", json.dumps({"status": "active"}))


def test_redis_node_write_with_ttl():
    mock_client = MagicMock()
    mount = RedisMount(redis_client=mock_client)
    node = mount.resolve("redis://cache:token#ttl=300")
    node.write({"token": "abc"})
    mock_client.setex.assert_called_once_with("cache:token", 300, json.dumps({"token": "abc"}))


def test_redis_node_read_returns_none_for_missing_key():
    mock_client = MagicMock()
    mock_client.get.return_value = None
    mount = RedisMount(redis_client=mock_client)
    node = mount.resolve("redis://missing:key")
    assert node.read() is None


# ---------------------------------------------------------------------------
# SnapshotManager
# ---------------------------------------------------------------------------

from app.infrastructure.storage.snapshot_manager import SnapshotManager


def _make_redis_mock():
    """Create a simple in-memory Redis mock using a dict."""
    store = {}

    mock = MagicMock()
    mock.set.side_effect = lambda k, v: store.update({k: v})
    mock.get.side_effect = lambda k: store.get(k)
    mock.delete.side_effect = lambda k: store.pop(k, None) is not None
    mock.keys.side_effect = lambda pattern: [
        k for k in store if _match_pattern(k, pattern)
    ]

    return mock


def _match_pattern(key: str, pattern: str) -> bool:
    """Minimal glob matching for the * wildcard."""
    if pattern.endswith("*"):
        return key.startswith(pattern[:-1])
    return key == pattern


def test_snapshot_manager_snapshot_and_restore():
    redis = _make_redis_mock()
    mgr = SnapshotManager(redis)
    uid = uuid4()

    key = mgr.snapshot(uid, version=1, payload={"name": "Alice"})
    assert "snapshots" in key

    record = mgr.restore(uid, version=1)
    assert record is not None
    assert record["payload"] == {"name": "Alice"}
    assert record["version"] == 1


def test_snapshot_manager_restore_missing_returns_none():
    redis = _make_redis_mock()
    mgr = SnapshotManager(redis)
    assert mgr.restore(uuid4(), version=99) is None


def test_snapshot_manager_list_snapshots():
    redis = _make_redis_mock()
    mgr = SnapshotManager(redis)
    uid = uuid4()
    mgr.snapshot(uid, version=1, payload={"v": 1})
    mgr.snapshot(uid, version=2, payload={"v": 2})

    keys = mgr.list_snapshots(uid)
    assert len(keys) == 2


def test_snapshot_manager_delete():
    redis = _make_redis_mock()
    mgr = SnapshotManager(redis)
    uid = uuid4()
    mgr.snapshot(uid, version=1, payload={})
    assert mgr.delete_snapshot(uid, version=1) is True
    assert mgr.restore(uid, version=1) is None


# ---------------------------------------------------------------------------
# BackupManager
# ---------------------------------------------------------------------------

from app.infrastructure.storage.backup_manager import BackupManager


def test_backup_manager_create_and_list():
    redis = _make_redis_mock()
    snap_mgr = SnapshotManager(redis)
    backup_mgr = BackupManager(redis, snap_mgr)

    uid = uuid4()
    snap_mgr.snapshot(uid, version=1, payload={"x": 1})
    snap_mgr.snapshot(uid, version=2, payload={"x": 2})

    backup_id = backup_mgr.create_backup(label="test-backup")
    assert backup_id

    backups = backup_mgr.list_backups()
    assert len(backups) == 1
    assert backups[0]["snapshot_count"] == 2
    assert backups[0]["label"] == "test-backup"


def test_backup_manager_restore():
    redis = _make_redis_mock()
    snap_mgr = SnapshotManager(redis)
    backup_mgr = BackupManager(redis, snap_mgr)

    uid = uuid4()
    snap_mgr.snapshot(uid, version=1, payload={"data": "original"})
    backup_id = backup_mgr.create_backup(label="checkpoint")

    # Delete the original snapshot
    snap_mgr.delete_snapshot(uid, version=1)
    assert snap_mgr.restore(uid, version=1) is None

    # Restore from backup
    count = backup_mgr.restore_backup(backup_id)
    assert count == 1
    assert snap_mgr.restore(uid, version=1) is not None


def test_backup_manager_delete():
    redis = _make_redis_mock()
    snap_mgr = SnapshotManager(redis)
    backup_mgr = BackupManager(redis, snap_mgr)

    backup_id = backup_mgr.create_backup(label="to-delete")
    assert backup_mgr.delete_backup(backup_id) is True
    assert backup_mgr.list_backups() == []


def test_backup_manager_restore_missing_raises():
    redis = _make_redis_mock()
    snap_mgr = SnapshotManager(redis)
    backup_mgr = BackupManager(redis, snap_mgr)

    with pytest.raises(ValueError, match="not found"):
        backup_mgr.restore_backup("nonexistent-id")


# ---------------------------------------------------------------------------
# ConcreteStorageManager
# ---------------------------------------------------------------------------

from app.infrastructure.storage.concrete_storage_manager import ConcreteStorageManager
from app.infrastructure.vfs.mount_registry import MountRegistry
from app.infrastructure.vfs.redis_mount import RedisMount


def test_concrete_storage_manager_ping_no_mounts():
    registry = MountRegistry()
    mgr = ConcreteStorageManager(registry)
    assert mgr.ping() is False


def test_concrete_storage_manager_ping_with_mount():
    registry = MountRegistry()
    registry.register("redis", RedisMount(redis_client=MagicMock()))
    mgr = ConcreteStorageManager(registry)
    assert mgr.ping() is True


def test_concrete_storage_manager_status():
    registry = MountRegistry()
    registry.register("redis", RedisMount(redis_client=MagicMock()))
    mgr = ConcreteStorageManager(registry)
    status = mgr.status()
    assert "redis" in status
    assert status["redis"]["has_client"] is True
    assert status["redis"]["mount_class"] == "RedisMount"
