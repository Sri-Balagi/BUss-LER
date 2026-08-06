"""Google Drive — Permissions Resource Handler"""

from __future__ import annotations
from typing import Any, Dict, List, Optional


class DrivePermissionsResource:
    """Handles ACL permission management against Google Drive API v3."""

    def __init__(self, service: Any) -> None:
        self._permissions = service.permissions()

    async def list_permissions(
        self,
        file_id: str,
        page_token: Optional[str] = None,
        page_size: int = 100,
    ) -> Dict[str, Any]:
        """List all permissions for a file or folder."""
        kwargs: Dict[str, Any] = {
            "fileId": file_id,
            "pageSize": min(page_size, 100),
            "fields": "nextPageToken,permissions(id,role,type,emailAddress,domain,displayName,photoLink,expirationTime,deleted,pendingOwner)",
            "supportsAllDrives": True,
        }
        if page_token:
            kwargs["pageToken"] = page_token
        return self._permissions.list(**kwargs).execute()

    async def get_permission(self, file_id: str, permission_id: str) -> Dict[str, Any]:
        """Get a specific permission entry."""
        return self._permissions.get(
            fileId=file_id,
            permissionId=permission_id,
            fields="id,role,type,emailAddress,domain,displayName,expirationTime",
            supportsAllDrives=True,
        ).execute()

    async def create_permission(
        self,
        file_id: str,
        role: str,
        grantee_type: str,
        email_address: Optional[str] = None,
        domain: Optional[str] = None,
        expiration_time: Optional[str] = None,
        send_notification: bool = True,
        email_message: Optional[str] = None,
        transfer_ownership: bool = False,
    ) -> Dict[str, Any]:
        """Grant a permission on a file/folder.

        Args:
            role: 'owner', 'organizer', 'fileOrganizer', 'writer', 'commenter', 'reader'
            grantee_type: 'user', 'group', 'domain', 'anyone'
        """
        body: Dict[str, Any] = {"role": role, "type": grantee_type}
        if email_address:
            body["emailAddress"] = email_address
        if domain:
            body["domain"] = domain
        if expiration_time:
            body["expirationTime"] = expiration_time

        kwargs: Dict[str, Any] = {
            "fileId": file_id,
            "body": body,
            "fields": "id,role,type,emailAddress,displayName",
            "supportsAllDrives": True,
            "sendNotificationEmail": send_notification,
            "transferOwnership": transfer_ownership,
        }
        if email_message:
            kwargs["emailMessage"] = email_message

        return self._permissions.create(**kwargs).execute()

    async def update_permission(
        self,
        file_id: str,
        permission_id: str,
        role: str,
        expiration_time: Optional[str] = None,
        transfer_ownership: bool = False,
    ) -> Dict[str, Any]:
        """Update a permission's role."""
        body: Dict[str, Any] = {"role": role}
        if expiration_time:
            body["expirationTime"] = expiration_time
        return self._permissions.update(
            fileId=file_id,
            permissionId=permission_id,
            body=body,
            fields="id,role,type,emailAddress",
            supportsAllDrives=True,
            transferOwnership=transfer_ownership,
        ).execute()

    async def delete_permission(self, file_id: str, permission_id: str) -> Dict[str, Any]:
        """Remove a permission from a file."""
        self._permissions.delete(
            fileId=file_id,
            permissionId=permission_id,
            supportsAllDrives=True,
        ).execute()
        return {"status": "DELETED", "file_id": file_id, "permission_id": permission_id}

    async def share_publicly(self, file_id: str, role: str = "reader") -> Dict[str, Any]:
        """Make a file publicly accessible."""
        return await self.create_permission(
            file_id=file_id,
            role=role,
            grantee_type="anyone",
            send_notification=False,
        )

    async def share_with_domain(
        self, file_id: str, domain: str, role: str = "reader"
    ) -> Dict[str, Any]:
        """Share a file with everyone in a domain."""
        return await self.create_permission(
            file_id=file_id,
            role=role,
            grantee_type="domain",
            domain=domain,
            send_notification=False,
        )
