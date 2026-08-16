from abc import ABC, abstractmethod


class IStorageManager(ABC):
    """
    Abstract interface for managing persistence operations across different concrete storage systems
    (e.g., PostgreSQL, Qdrant).
    """
    @abstractmethod
    def ping(self) -> bool:
        """Verify connection to the underlying storage engines."""
        pass
