"""Google Drive — Folders & Shared Drives Resource Handler"""

from __future__ import annotations
from typing import Any, Dict, List, Optional


class DriveFoldersResource:
    """Handles folder and shared drive operations against Google Drive API v3."""

    def __init__(self, service: Any) -> None:
        self._files = service.files()
        self._drives = service.drives()

    async def create_folder(
        self,
        name: str,
        parent_folder_id: Optional[str] = None,
        drive_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a folder."""
        body: Dict[str, Any] = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
        }
        parents = []
        if parent_folder_id:
            parents.append(parent_folder_id)
        if drive_id and not parent_folder_id:
            parents.append(drive_id)
        if parents:
            body["parents"] = parents

        return self._files.create(
            body=body,
            fields="id,name,mimeType,parents,webViewLink,createdTime",
            supportsAllDrives=True,
        ).execute()

    async def list_folder_contents(
        self,
        folder_id: str,
        page_token: Optional[str] = None,
        page_size: int = 100,
        order_by: str = "folder,name",
    ) -> Dict[str, Any]:
        """List the contents of a folder."""
        return self._files.list(
            q=f"'{folder_id}' in parents and trashed=false",
            pageSize=min(page_size, 1000),
            pageToken=page_token or "",
            orderBy=order_by,
            fields="nextPageToken,files(id,name,mimeType,size,parents,webViewLink,modifiedTime,trashed)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()

    async def get_folder(self, folder_id: str) -> Dict[str, Any]:
        """Get folder metadata."""
        return self._files.get(
            fileId=folder_id,
            fields="id,name,mimeType,parents,webViewLink,createdTime,modifiedTime,owners,capabilities",
            supportsAllDrives=True,
        ).execute()

    async def delete_folder(self, folder_id: str) -> Dict[str, Any]:
        """Delete a folder and all its contents."""
        self._files.delete(fileId=folder_id, supportsAllDrives=True).execute()
        return {"status": "DELETED", "folder_id": folder_id}

    # ── Shared Drives ─────────────────────────────────────────────────────────

    async def list_shared_drives(
        self,
        page_token: Optional[str] = None,
        page_size: int = 100,
        query: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List all shared drives accessible to the authenticated user."""
        kwargs: Dict[str, Any] = {
            "pageSize": min(page_size, 100),
            "fields": "nextPageToken,drives(id,name,kind,colorRgb,backgroundImageLink,createdTime,restrictions)",
        }
        if page_token:
            kwargs["pageToken"] = page_token
        if query:
            kwargs["q"] = query
        return self._drives.list(**kwargs).execute()

    async def get_shared_drive(self, drive_id: str) -> Dict[str, Any]:
        """Get shared drive metadata."""
        return self._drives.get(
            driveId=drive_id,
            fields="id,name,colorRgb,backgroundImageLink,createdTime,restrictions,capabilities",
        ).execute()

    async def create_shared_drive(self, name: str) -> Dict[str, Any]:
        """Create a new shared drive."""
        import uuid
        request_id = str(uuid.uuid4())
        return self._drives.create(
            requestId=request_id,
            body={"name": name},
            fields="id,name,createdTime",
        ).execute()

    async def update_shared_drive(
        self, drive_id: str, name: Optional[str] = None, restrictions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Update shared drive settings."""
        body: Dict[str, Any] = {}
        if name:
            body["name"] = name
        if restrictions:
            body["restrictions"] = restrictions
        return self._drives.update(
            driveId=drive_id,
            body=body,
            fields="id,name,restrictions",
        ).execute()

    async def delete_shared_drive(self, drive_id: str) -> Dict[str, Any]:
        """Delete a shared drive (must be empty)."""
        self._drives.delete(driveId=drive_id).execute()
        return {"status": "DELETED", "drive_id": drive_id}

    async def list_my_drive_root(self, page_size: int = 100) -> Dict[str, Any]:
        """List items at the root of My Drive."""
        return self._files.list(
            q="'root' in parents and trashed=false",
            pageSize=min(page_size, 1000),
            orderBy="folder,name",
            fields="nextPageToken,files(id,name,mimeType,size,webViewLink,modifiedTime)",
            supportsAllDrives=False,
        ).execute()
