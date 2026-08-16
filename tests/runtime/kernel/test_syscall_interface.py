import pytest

from app.runtime.kernel.syscall import ISyscallInterface, KernelRing


class DummySyscall(ISyscallInterface):
    def start_session(self, context): return None
    def stop_session(self, session_id): pass
    def suspend(self, pid): pass
    def resume(self, pid): pass
    def allocate(self, resource_type, amount): return True
    def release(self, resource_type, amount): pass
    def read(self, uri): return None
    def write(self, uri, content): pass
    def search(self, query, context=None): return None
    def invoke_capability(self, capability_uri, payload): return None
    def request_approval(self, approval_type, context): return True
    def publish_event(self, topic, event_data): pass
    def subscribe(self, topic, callback): pass
    def log(self, level, message): pass
    def checkpoint(self, pid): return "uri"
    def restore(self, pid, checkpoint_uri): return True

def test_syscall_interface_instantiation():
    # Should not raise exception
    syscall = DummySyscall()
    assert syscall is not None

def test_kernel_rings_exist():
    assert KernelRing.RING_0 == 0
    assert KernelRing.RING_1 == 1
    assert KernelRing.RING_2 == 2
    assert KernelRing.RING_3 == 3
