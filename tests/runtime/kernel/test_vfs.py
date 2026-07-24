import pytest

from app.infrastructure.vfs.vfs import IVirtualFileSystem, MountManager, PathResolver


class DummyVFS(IVirtualFileSystem):
    def mount_manager(self): return None
    def path_resolver(self): return None
    def read(self, uri): return "data"
    def write(self, uri, content): pass

def test_vfs_instantiation():
    vfs = DummyVFS()
    assert vfs.read("twin://123/memory") == "data"
