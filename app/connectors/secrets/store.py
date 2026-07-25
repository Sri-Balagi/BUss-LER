"""Secret store interface."""
from __future__ import annotations
from abc import ABC, abstractmethod
from app.connectors.secrets.models import SecretRecord, SecretType


class ISecretStore(ABC):
    """Abstract interface for connector secret storage."""

    @abstractmethod
    async def store(self, key: str, record: SecretRecord) -> None:
        """Persist an encrypted secret record."""

    @abstractmethod
    async def retrieve(self, key: str) -> SecretRecord | None:
        """Retrieve a secret record by key. Returns None if not found."""

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Permanently remove a secret from the store."""

    @abstractmethod
    async def rotate(self, key: str, new_value: str) -> SecretRecord:
        """Replace the secret value and update rotation timestamp."""

    @abstractmethod
    async def list_by_connector(
        self,
        connector_id: str,
        profile_id: str = "default",
    ) -> list[SecretRecord]:
        """List all secrets for a connector+profile (values masked)."""

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if a secret key exists in the store."""
