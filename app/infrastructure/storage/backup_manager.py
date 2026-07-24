"""
Wave-2 Milestone 4: Storage Layer — Backup Manager
====================================================
BackupManager provides full-dataset backup and restore for BizOS
by sweeping all snapshots and compressing them into a backup archive.

Design
------
- Backups are stored as JSON archives in Redis under:
  ``backups:<backup_id>``
- Each backup record contains: backup_id, timestamp, list of snapshots.
- In Milestone 5+ this will upload to Supabase Storage / S3 for durability.
- Restore replays all snapshots from a backup archive via SnapshotManager.
"""
from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from app.infrastructure.storage.snapshot_manager import SnapshotManager


class BackupManager:
    """
    Creates and restores full-system backups from the snapshot layer.

    Parameters
    ----------
    redis_client:
        A synchronous redis.Redis client.
    snapshot_manager:
        The SnapshotManager instance used to read individual snapshots.
    """

    def __init__(self, redis_client: Any, snapshot_manager: SnapshotManager) -> None:
        self._redis = redis_client
        self._snapshots = snapshot_manager
        self._prefix = "backups"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_backup(self, label: str = "") -> str:
        """
        Sweep all snapshot keys from Redis and consolidate into one backup archive.

        Parameters
        ----------
        label : Optional human-readable label for the backup.

        Returns
        -------
        str : the backup_id (UUID string).
        """
        backup_id = str(uuid4())
        all_keys = self._redis.keys("snapshots:*")

        entries = []
        for key in all_keys:
            raw = self._redis.get(key)
            if raw:
                try:
                    entries.append(json.loads(raw))
                except json.JSONDecodeError:
                    pass

        record = {
            "backup_id": backup_id,
            "label": label,
            "created_at": datetime.now(UTC).isoformat(),
            "snapshot_count": len(entries),
            "snapshots": entries,
        }

        self._redis.set(f"{self._prefix}:{backup_id}", json.dumps(record))
        return backup_id

    def restore_backup(self, backup_id: str) -> int:
        """
        Replay all snapshots from a backup archive via the SnapshotManager.

        Returns the number of snapshots restored.
        """
        raw = self._redis.get(f"{self._prefix}:{backup_id}")
        if raw is None:
            raise ValueError(f"BackupManager: backup '{backup_id}' not found.")

        record = json.loads(raw)
        restored = 0
        for entry in record.get("snapshots", []):
            from uuid import UUID
            self._snapshots.snapshot(
                object_id=UUID(entry["object_id"]),
                version=entry["version"],
                payload=entry["payload"],
            )
            restored += 1

        return restored

    def list_backups(self) -> list[dict]:
        """
        Return metadata for all backups (without full snapshot payloads).
        """
        keys = self._redis.keys(f"{self._prefix}:*")
        result = []
        for key in sorted(keys):
            raw = self._redis.get(key)
            if raw:
                try:
                    record = json.loads(raw)
                    result.append({
                        "backup_id": record["backup_id"],
                        "label": record.get("label", ""),
                        "created_at": record["created_at"],
                        "snapshot_count": record["snapshot_count"],
                    })
                except (json.JSONDecodeError, KeyError):
                    pass
        return result

    def delete_backup(self, backup_id: str) -> bool:
        """Delete a backup archive. Returns True if the key existed."""
        return bool(self._redis.delete(f"{self._prefix}:{backup_id}"))
