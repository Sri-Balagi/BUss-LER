from abc import ABC, abstractmethod
from typing import Any


class IRedisProvider(ABC):
    @abstractmethod
    async def get(self, key: str) -> str | None: pass

    @abstractmethod
    async def set(self, key: str, value: str, ttl: int | None = None): pass

    @abstractmethod
    async def delete(self, key: str): pass

class IMessageQueue(ABC):
    @abstractmethod
    async def push(self, queue: str, message: dict): pass

    @abstractmethod
    async def pop(self, queue: str, timeout: int = 5) -> dict | None: pass

    @abstractmethod
    async def ack(self, message_id: str): pass

    @abstractmethod
    async def nack(self, message_id: str): pass

    @abstractmethod
    async def heartbeat(self, worker_id: str, timestamp: float): pass

class IDatabaseProvider(ABC):
    @abstractmethod
    async def execute(self, query: str, params: tuple = None) -> Any: pass

    @abstractmethod
    async def fetch(self, query: str, params: tuple = None) -> list[dict[str, Any]]: pass

class IObjectStorage(ABC):
    @abstractmethod
    async def upload(self, bucket: str, key: str, data: bytes): pass

    @abstractmethod
    async def download(self, bucket: str, key: str) -> bytes: pass
