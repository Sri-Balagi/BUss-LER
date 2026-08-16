from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class IVirtualNode(BaseModel, ABC):
    """
    Represents an addressable node (file, artifact, memory vector) within the BizOS Virtual Filesystem.
    """
    path: str
    metadata: dict[str, Any]

    @abstractmethod
    def read(self) -> Any:
        pass

    @abstractmethod
    def write(self, content: Any) -> None:
        pass

class IVirtualMount(ABC):
    """
    Represents a mounted storage driver (e.g., PostgreSQL, Qdrant, S3, Local)
    that satisfies VFS node resolution for a specific scheme/prefix.
    """

    @property
    @abstractmethod
    def scheme(self) -> str:
        """e.g., 'twin://', 'memory://', 'artifact://'"""
        pass

    @abstractmethod
    def resolve(self, path: str) -> IVirtualNode:
        pass

class MountManager(ABC):
    """
    Manages registered IVirtualMount instances.
    """

    @abstractmethod
    def mount(self, prefix: str, mount: IVirtualMount) -> None:
        pass

    @abstractmethod
    def unmount(self, prefix: str) -> None:
        pass

    @abstractmethod
    def get_mount(self, prefix: str) -> IVirtualMount | None:
        pass

class PathResolver(ABC):
    """
    Parses VFS URIs and routes them to the correct IVirtualMount.
    """

    @abstractmethod
    def resolve(self, uri: str) -> IVirtualNode:
        """
        Example URI: twin://<uuid>/memory/semantic/123
        Resolves to the appropriate mount and returns the virtual node.
        """
        pass

class IVirtualFileSystem(ABC):
    """
    The unified interface for the Virtual Filesystem (VFS).
    Used by Agents and Capabilities to interact with storage completely agnostic
    of the underlying infrastructure (Postgres, Redis, Qdrant).
    """

    @abstractmethod
    def mount_manager(self) -> MountManager:
        pass

    @abstractmethod
    def path_resolver(self) -> PathResolver:
        pass

    @abstractmethod
    def read(self, uri: str) -> Any:
        pass

    @abstractmethod
    def write(self, uri: str, content: Any) -> None:
        pass
