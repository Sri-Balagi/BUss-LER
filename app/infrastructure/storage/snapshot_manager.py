"""
Wave-2 Milestone 4: Storage Layer — Snapshot Manager
======================================================
SnapshotManager captures and restores point-in-time snapshots of BizObjects.

Design
------
- Snapshots are JSON-serialised copies of a BizObject's state stored in Redis.
- URI format: ``redis://snapshots:<object_id>:<version>``
- Snapshots are immutable once written. Restoring creates a new BizObject
  instance from the snapshot payload without mutating the original.
- In Milestone 5+ this will delegate to an S3/Supabase Storage backend for
  long-term archival.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import UUID


class SnapshotManager:
    """
    Captures and restores BizObject snapshots via the Redis VFS mount.

    Parameters
    ----------
    redis_client:
        A synchronous redis.Redis client. Injected via DI.
    """

    def __init__(self, redis_client: Any) -> None:
        self._redis = redis_client
        self._prefix = "snapshots"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def snapshot(self, object_id: UUID, version: int, payload: dict) -> str:
        """
        Persist a snapshot and return the snapshot key.

        Parameters
        ----------
        object_id : UUID of the BizObject being snapshotted.
        version   : The BizObject.version at time of snapshot.
        payload   : The full serialised state of the BizObject (dict).

        Returns
        -------
        str : the Redis key where the snapshot is stored.
        """
        key = self._make_key(object_id, version)
        record = {
            "object_id": str(object_id),
            "version": version,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
        }
        self._redis.set(key, json.dumps(record))
        return key

    def restore(self, object_id: UUID, version: int) -> dict | None:
        """
        Retrieve a snapshot for the given object_id and version.

        Returns the full snapshot record, or None if not found.
        """
        key = self._make_key(object_id, version)
        raw = self._redis.get(key)
        if raw is None:
            return None
        return json.loads(raw)

    def list_snapshots(self, object_id: UUID) -> list[str]:
        """
        List all snapshot keys for a given object_id.
        Returns keys in chronological order (by version number embedded in key).
        """
        pattern = f"{self._prefix}:{object_id}:*"
        keys = self._redis.keys(pattern)
        return sorted(keys)

    def delete_snapshot(self, object_id: UUID, version: int) -> bool:
        """Delete a specific snapshot. Returns True if the key existed."""
        key = self._make_key(object_id, version)
        return bool(self._redis.delete(key))

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _make_key(self, object_id: UUID, version: int) -> str:
        return f"{self._prefix}:{object_id}:{version}"
