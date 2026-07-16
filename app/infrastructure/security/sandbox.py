import sys
import os
import logging
from typing import Set

from app.domain.security.interfaces import ISandboxPolicyEnforcer
from app.domain.security.models import SandboxPolicy

logger = logging.getLogger(__name__)

class PythonAuditHookEnforcer(ISandboxPolicyEnforcer):
    """
    Enforces a SandboxPolicy using sys.addaudithook.
    This provides runtime policy enforcement within a Python process, complementing OS-level isolation.
    """
    
    def __init__(self):
        self._policy = None
        self._allowed_dirs: Set[str] = set()

    def enforce(self, policy: SandboxPolicy) -> None:
        """
        Applies the security boundaries described by the SandboxPolicy via an audit hook.
        This must be called inside the isolated subprocess before executing user code.
        """
        if self._policy is not None:
            raise RuntimeError("Sandbox enforcement is already active in this process.")
            
        self._policy = policy
        
        if policy.allowed_directories:
            self._allowed_dirs = {os.path.normcase(os.path.abspath(d)) for d in policy.allowed_directories}
            
        sys.addaudithook(self._audit_hook)
        logger.debug("sandbox_audit_hook_installed", extra={"policy": str(policy)})
        
    def _is_path_allowed(self, target_path: str) -> bool:
        """Checks if a path falls within the allowed directories."""
        if not self._allowed_dirs:
            # If no specific allowed directories, we might deny all or assume open depending on design.
            # Default secure: Deny if no explicit allow-list provided.
            return False
            
        abs_target = os.path.normcase(os.path.abspath(target_path))
        for allowed in self._allowed_dirs:
            if abs_target.startswith(allowed):
                return True
        return False

    def _audit_hook(self, event: str, args: tuple) -> None:
        """
        The actual hook invoked by the Python runtime for sensitive operations.
        """
        
        # 1. Subprocess Execution
        if event == "os.system" or event.startswith("subprocess."):
            if not self._policy.allow_subprocess:
                raise PermissionError(f"Sandbox policy violation: subprocess execution blocked ({event})")
                
        # 2. Network Access
        if event == "socket.__new__":
            if not self._policy.allow_network:
                raise PermissionError(f"Sandbox policy violation: network access blocked ({event})")
                
        # 3. Environment Variables
        if event in ("os.environ", "os.putenv", "os.unsetenv"):
            if not self._policy.allow_environment_variables:
                raise PermissionError(f"Sandbox policy violation: environment variable access blocked ({event})")
                
        # 4. File Access (open)
        if event == "open":
            # args[0] is the path
            # We only enforce this if allowed_directories is strictly provided.
            # If allowed_directories is empty, we assume no file access is permitted except standard libs.
            # Note: standard library imports trigger 'open', so strict file blocking requires careful tuning.
            # For this milestone, we only block if it explicitly violates the allowed_dirs if one is set.
            path = args[0]
            if isinstance(path, str) or isinstance(path, bytes):
                try:
                    path_str = os.fspath(path)
                except Exception:
                    return # Ignore unparseable paths
                    
                # Check against allowed directories
                if self._allowed_dirs:
                    if not self._is_path_allowed(path_str):
                        raise PermissionError(f"Sandbox policy violation: file access blocked ({path_str})")
