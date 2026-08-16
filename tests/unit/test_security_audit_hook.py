import os
from unittest.mock import patch

import pytest

from app.domain.security.models import SandboxPolicy
from app.infrastructure.security.sandbox import PythonAuditHookEnforcer


def test_audit_hook_subprocess():
    enforcer = PythonAuditHookEnforcer()
    enforcer._policy = SandboxPolicy(allow_subprocess=False)

    with pytest.raises(PermissionError, match="subprocess execution blocked"):
        enforcer._audit_hook("os.system", ("echo",))

    with pytest.raises(PermissionError, match="subprocess execution blocked"):
        enforcer._audit_hook("subprocess.run", ([],))

def test_audit_hook_network():
    enforcer = PythonAuditHookEnforcer()
    enforcer._policy = SandboxPolicy(allow_network=False)

    with pytest.raises(PermissionError, match="network access blocked"):
        enforcer._audit_hook("socket.__new__", ())

def test_audit_hook_env_vars():
    enforcer = PythonAuditHookEnforcer()
    enforcer._policy = SandboxPolicy(allow_environment_variables=False)

    with pytest.raises(PermissionError, match="environment variable access blocked"):
        enforcer._audit_hook("os.environ", ())

def test_audit_hook_file_access_blocked():
    enforcer = PythonAuditHookEnforcer()
    enforcer._policy = SandboxPolicy(allowed_directories=["/safe/dir"])
    enforcer._allowed_dirs = {os.path.normcase(os.path.abspath("/safe/dir"))}

    with pytest.raises(PermissionError, match="file access blocked"):
        enforcer._audit_hook("open", ("/unsafe/dir/file.txt",))

def test_audit_hook_file_access_allowed():
    enforcer = PythonAuditHookEnforcer()
    enforcer._policy = SandboxPolicy(allowed_directories=["/safe/dir"])
    enforcer._allowed_dirs = {os.path.normcase(os.path.abspath("/safe/dir"))}

    # Should not raise
    enforcer._audit_hook("open", ("/safe/dir/file.txt",))

def test_audit_hook_file_access_no_strict_dirs():
    enforcer = PythonAuditHookEnforcer()
    enforcer._policy = SandboxPolicy()

    # Empty allowed_directories means no strict enforcement on open in our implementation
    # Wait, the code says: if self._allowed_dirs: ... else: does nothing for open
    enforcer._audit_hook("open", ("/unsafe/dir/file.txt",))

@patch("sys.addaudithook")
def test_enforce_installs_hook(mock_addaudithook):
    enforcer = PythonAuditHookEnforcer()
    policy = SandboxPolicy(allowed_directories=["/test"])

    enforcer.enforce(policy)

    mock_addaudithook.assert_called_once_with(enforcer._audit_hook)
    assert len(enforcer._allowed_dirs) == 1

    with pytest.raises(RuntimeError, match="already active"):
        enforcer.enforce(policy)

def test_is_path_allowed():
    enforcer = PythonAuditHookEnforcer()
    assert not enforcer._is_path_allowed("/test")

    enforcer._allowed_dirs = {os.path.normcase(os.path.abspath("/safe/dir"))}
    assert enforcer._is_path_allowed("/safe/dir/file.txt")
    assert not enforcer._is_path_allowed("/unsafe/dir/file.txt")

def test_audit_hook_unparseable_path():
    enforcer = PythonAuditHookEnforcer()
    enforcer._policy = SandboxPolicy(allowed_directories=["/safe/dir"])
    enforcer._allowed_dirs = {os.path.normcase(os.path.abspath("/safe/dir"))}

    # Not a string or bytes, should be ignored
    enforcer._audit_hook("open", (123,))

    # Something that fails os.fspath
    class BadPath:
        def __fspath__(self):
            raise Exception("bad")

    enforcer._audit_hook("open", (BadPath(),))
