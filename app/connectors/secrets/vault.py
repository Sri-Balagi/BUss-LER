"""
In-memory secret vault (development/testing implementation).

For production, replace with a Postgres-backed or HashiCorp Vault implementation.
The interface is identical — swap via DI.
"""
from __future__ import annotations

import logging
from datetime import UTC, datetime

from pydantic import SecretStr

from app.connectors.exceptions.errors import SecretNotFoundError, SecretStorageError
from app.connectors.secrets.models import SecretRecord
from app.connectors.secrets.store import ISecretStore

logger = logging.getLogger(__name__)


class InMemorySecretVault(ISecretStore):
    """
    In-memory secret vault for development and testing.

    NOT suitable for production — secrets are not encrypted at rest.
    """

    def __init__(self) -> None:
        self._store: dict[str, SecretRecord] = {}

    async def store(self, key: str, record: SecretRecord) -> None:
        self._store[key] = record
        logger.debug("Secret stored key=%s connector=%s", key, record.connector_id)

    async def retrieve(self, key: str) -> SecretRecord | None:
        return self._store.get(key)

    async def delete(self, key: str) -> None:
        if key not in self._store:
            raise SecretNotFoundError(f"Secret key {key!r} not found")
        del self._store[key]

    async def rotate(self, key: str, new_value: str) -> SecretRecord:
        existing = self._store.get(key)
        if existing is None:
            raise SecretNotFoundError(f"Secret key {key!r} not found")
        updated = existing.model_copy(
            update={
                "value": SecretStr(new_value),
                "rotated_at": datetime.now(UTC),
            }
        )
        self._store[key] = updated
        logger.info("Secret rotated key=%s", key)
        return updated

    async def list_by_connector(
        self,
        connector_id: str,
        profile_id: str = "default",
    ) -> list[SecretRecord]:
        return [
            r for r in self._store.values()
            if r.connector_id == connector_id and r.profile_id == profile_id
        ]

    async def exists(self, key: str) -> bool:
        return key in self._store
