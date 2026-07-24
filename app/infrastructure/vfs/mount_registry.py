
from app.infrastructure.vfs.vfs import IVirtualMount


class MountRegistry:
    """
    Maintains a registry of all active IVirtualMounts in the OS.
    Replaces the generic MountManager from earlier iterations.
    """
    def __init__(self):
        self._mounts: dict[str, IVirtualMount] = {}

    def register(self, scheme: str, mount: IVirtualMount) -> None:
        self._mounts[scheme] = mount

    def get_mount(self, scheme: str) -> IVirtualMount | None:
        return self._mounts.get(scheme)
