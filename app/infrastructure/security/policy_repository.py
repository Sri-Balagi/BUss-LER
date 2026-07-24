
from app.domain.security.interfaces import IPolicyRepository
from app.domain.security.permissions import SystemPermission


class InMemoryPolicyRepository(IPolicyRepository):
    """
    In-memory implementation of the policy repository.
    Maps roles to a set of explicit SystemPermissions.
    """

    def __init__(self):
        # A static role-to-permission mapping for this milestone
        self._role_permissions = {
            "system:admin": {
                SystemPermission.SYSTEM_ADMIN,
                SystemPermission.WORKFLOW_READ,
                SystemPermission.WORKFLOW_WRITE,
                SystemPermission.WORKFLOW_EXECUTE,
                SystemPermission.AGENT_READ,
                SystemPermission.AGENT_WRITE,
                SystemPermission.AGENT_INVOKE,
                SystemPermission.ARTIFACT_READ,
                SystemPermission.ARTIFACT_WRITE,
                SystemPermission.MEMORY_READ,
                SystemPermission.MEMORY_WRITE,
            },
            "developer": {
                SystemPermission.WORKFLOW_READ,
                SystemPermission.WORKFLOW_WRITE,
                SystemPermission.WORKFLOW_EXECUTE,
                SystemPermission.AGENT_READ,
                SystemPermission.AGENT_WRITE,
                SystemPermission.ARTIFACT_READ,
                SystemPermission.ARTIFACT_WRITE,
                SystemPermission.MEMORY_READ,
            },
            "agent": {
                SystemPermission.WORKFLOW_EXECUTE,
                SystemPermission.ARTIFACT_READ,
                SystemPermission.ARTIFACT_WRITE,
                SystemPermission.MEMORY_READ,
                SystemPermission.MEMORY_WRITE,
            },
            "viewer": {
                SystemPermission.WORKFLOW_READ,
                SystemPermission.AGENT_READ,
                SystemPermission.ARTIFACT_READ,
                SystemPermission.MEMORY_READ,
            }
        }

    async def get_permissions_for_roles(self, roles: list[str]) -> set[str]:
        """
        Resolves the roles to a flat set of permission string values.
        """
        permissions = set()
        for role in roles:
            # We map role name to a set of enums, then extract their string values
            role_perms = self._role_permissions.get(role, set())
            permissions.update(p.value for p in role_perms)

        return permissions
