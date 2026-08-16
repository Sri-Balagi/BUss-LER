from urllib.parse import urlparse

from app.infrastructure.vfs.mount_registry import MountRegistry
from app.infrastructure.vfs.vfs import IVirtualNode


class MountResolver:
    """
    Resolves VFS URIs to concrete IVirtualNodes using the MountRegistry.
    """
    def __init__(self, registry: MountRegistry):
        self.registry = registry

    def resolve(self, uri: str) -> IVirtualNode:
        """
        Parses the URI (e.g., 'twin://uuid/memory') and delegates to the correct mount.
        """
        parsed = urlparse(uri)
        scheme = parsed.scheme

        mount = self.registry.get_mount(scheme)
        if not mount:
            raise ValueError(f"No mount registered for scheme '{scheme}'")

        return mount.resolve(uri)
