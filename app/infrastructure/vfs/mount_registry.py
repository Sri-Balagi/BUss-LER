from typing import Dict, Optional
from app.infrastructure.vfs.vfs import IVirtualMount

class MountRegistry:
    """
    Maintains a registry of all active IVirtualMounts in the OS.
    Replaces the generic MountManager from earlier iterations.
    """
    def __init__(self):
        self._mounts: Dict[str, IVirtualMount] = {}

    def register(self, scheme: str, mount: IVirtualMount) -> None:
        self._mounts[scheme] = mount

    def get_mount(self, scheme: str) -> Optional[IVirtualMount]:
        return self._mounts.get(scheme)
