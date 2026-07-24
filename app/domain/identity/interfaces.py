from abc import ABC, abstractmethod

from app.domain.identity.api_key import APIKey


class IAPIKeyRepository(ABC):
    """
    Interface for looking up API keys by their prefix.
    Hash verification is explicitly NOT the responsibility of this repository,
    but rather the identity provider interacting with IHasher.
    """

    @abstractmethod
    async def get_by_prefix(self, prefix: str) -> APIKey | None:
        """
        Retrieves an API key based on its public prefix.
        Returns None if the key doesn't exist.
        """
        pass

    @abstractmethod
    async def save(self, api_key: APIKey) -> None:
        """
        Saves or updates an API Key.
        """
        pass
