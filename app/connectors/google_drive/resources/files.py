"""Google Drive — Files Resource Handler

Handles all file-level operations against the Google Drive API v3.
Real API calls — no stubs, no mocks.
"""

from __future__ import annotations

import io
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)

# MIME type conversion map: Google Workspace → standard formats
GOOGLE_EXPORT_FORMATS: Dict[str, Dict[str, str]] = {
    "application/vnd.google-apps.document": {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "txt": "text/plain",
        "html": "text/html",
        "md": "text/markdown",
        "odt": "application/vnd.oasis.opendocument.text",
        "rtf": "application/rtf",
    },
    "application/vnd.google-apps.spreadsheet": {
        "pdf": "application/pdf",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "csv": "text/csv",
        "ods": "application/x-vnd.oasis.opendocument.spreadsheet",
        "tsv": "text/tab-separated-values",
    },
    "application/vnd.google-apps.presentation": {
        "pdf": "application/pdf",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "odp": "application/vnd.oasis.opendocument.presentation",
        "png": "image/png",
    },
    "application/vnd.google-apps.drawing": {
        "pdf": "application/pdf",
        "png": "image/png",
        "svg": "image/svg+xml",
        "jpeg": "image/jpeg",
    },
}


class DriveFilesResource:
    """Handles all file operations against Google Drive API v3."""

    def __init__(self, service: Any) -> None:
        """
        Args:
            service: Authenticated Google Drive API service object
                     (from googleapiclient.discovery.build()).
        """
        self._files = service.files()

    async def list_files(
        self,
        query: Optional[str] = None,
        page_token: Optional[str] = None,
        page_size: int = 100,
        order_by: str = "modifiedTime desc",
        drive_id: Optional[str] = None,
        include_items_from_all_drives: bool = True,
        fields: str = "nextPageToken,files(id,name,mimeType,size,parents,owners,webViewLink,webContentLink,createdTime,modifiedTime,trashed,starred,shared,description,version,shortcutDetails)",
    ) -> Dict[str, Any]:
        """List files with full metadata. Supports shared drives."""
        kwargs: Dict[str, Any] = {
            "pageSize": min(page_size, 1000),
            "orderBy": order_by,
            "fields": fields,
            "supportsAllDrives": True,
            "includeItemsFromAllDrives": include_items_from_all_drives,
        }
        if query:
            kwargs["q"] = query
        if page_token:
            kwargs["pageToken"] = page_token
        if drive_id:
            kwargs["driveId"] = drive_id
            kwargs["corpora"] = "drive"

        result = self._files.list(**kwargs).execute()
        return result

    async def get_file(
        self,
        file_id: str,
        fields: str = "id,name,mimeType,size,parents,owners,webViewLink,webContentLink,createdTime,modifiedTime,trashed,starred,shared,description,version,shortcutDetails,permissions,capabilities",
    ) -> Dict[str, Any]:
        """Get a single file by ID with full metadata."""
        return (
            self._files.get(
                fileId=file_id,
                fields=fields,
                supportsAllDrives=True,
            ).execute()
        )

    async def search_files(
        self,
        query: str,
        page_size: int = 100,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Full-text search across Drive using Drive query syntax."""
        return await self.list_files(query=query, page_size=page_size, page_token=page_token)

    async def upload_file(
        self,
        name: str,
        content: bytes,
        mime_type: str,
        parent_folder_id: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upload a file using resumable multipart upload."""
        from googleapiclient.http import MediaIoBaseUpload

        file_metadata: Dict[str, Any] = {"name": name}
        if parent_folder_id:
            file_metadata["parents"] = [parent_folder_id]
        if description:
            file_metadata["description"] = description

        media = MediaIoBaseUpload(
            io.BytesIO(content),
            mimetype=mime_type,
            resumable=True,
            chunksize=5 * 1024 * 1024,  # 5MB chunks
        )

        return (
            self._files.create(
                body=file_metadata,
                media_body=media,
                fields="id,name,mimeType,size,webViewLink,parents,createdTime",
                supportsAllDrives=True,
            ).execute()
        )

    async def update_file(
        self,
        file_id: str,
        content: Optional[bytes] = None,
        mime_type: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update file content and/or metadata."""
        from googleapiclient.http import MediaIoBaseUpload

        file_metadata: Dict[str, Any] = {}
        if name:
            file_metadata["name"] = name
        if description:
            file_metadata["description"] = description

        if content and mime_type:
            media = MediaIoBaseUpload(
                io.BytesIO(content),
                mimetype=mime_type,
                resumable=True,
            )
            return (
                self._files.update(
                    fileId=file_id,
                    body=file_metadata,
                    media_body=media,
                    fields="id,name,mimeType,size,modifiedTime",
                    supportsAllDrives=True,
                ).execute()
            )
        else:
            return (
                self._files.update(
                    fileId=file_id,
                    body=file_metadata,
                    fields="id,name,mimeType,modifiedTime",
                    supportsAllDrives=True,
                ).execute()
            )

    async def download_file(self, file_id: str) -> bytes:
        """Download a file's raw content."""
        from googleapiclient.http import MediaIoBaseDownload

        request = self._files.get_media(fileId=file_id, supportsAllDrives=True)
        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, request, chunksize=10 * 1024 * 1024)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        return buffer.getvalue()

    async def export_file(self, file_id: str, export_format: str, mime_type: str) -> bytes:
        """Export a Google Workspace file (Docs→PDF, Sheets→XLSX, etc.)."""
        from googleapiclient.http import MediaIoBaseDownload

        request = self._files.export_media(fileId=file_id, mimeType=mime_type)
        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, request, chunksize=10 * 1024 * 1024)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        return buffer.getvalue()

    async def delete_file(self, file_id: str) -> Dict[str, Any]:
        """Permanently delete a file (bypasses trash)."""
        self._files.delete(fileId=file_id, supportsAllDrives=True).execute()
        return {"status": "DELETED", "file_id": file_id}

    async def trash_file(self, file_id: str) -> Dict[str, Any]:
        """Move file to trash (recoverable)."""
        result = self._files.update(
            fileId=file_id,
            body={"trashed": True},
            fields="id,name,trashed",
            supportsAllDrives=True,
        ).execute()
        return result

    async def restore_from_trash(self, file_id: str) -> Dict[str, Any]:
        """Restore a trashed file."""
        return self._files.update(
            fileId=file_id,
            body={"trashed": False},
            fields="id,name,trashed",
            supportsAllDrives=True,
        ).execute()

    async def empty_trash(self) -> Dict[str, Any]:
        """Permanently delete all trashed files."""
        self._files.emptyTrash().execute()
        return {"status": "TRASH_EMPTIED"}

    async def copy_file(
        self,
        file_id: str,
        name: Optional[str] = None,
        parent_folder_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Copy a file to a new location."""
        body: Dict[str, Any] = {}
        if name:
            body["name"] = name
        if parent_folder_id:
            body["parents"] = [parent_folder_id]
        return self._files.copy(
            fileId=file_id,
            body=body,
            fields="id,name,mimeType,parents,webViewLink",
            supportsAllDrives=True,
        ).execute()

    async def move_file(self, file_id: str, new_parent_id: str) -> Dict[str, Any]:
        """Move a file to a different folder."""
        # Get current parents
        file_data = self._files.get(
            fileId=file_id, fields="parents", supportsAllDrives=True
        ).execute()
        previous_parents = ",".join(file_data.get("parents", []))

        return self._files.update(
            fileId=file_id,
            addParents=new_parent_id,
            removeParents=previous_parents,
            fields="id,name,parents",
            supportsAllDrives=True,
        ).execute()

    async def get_export_formats(self, mime_type: str) -> Dict[str, str]:
        """Get available export formats for a Google Workspace MIME type."""
        return GOOGLE_EXPORT_FORMATS.get(mime_type, {})

    async def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """Get extended metadata including capabilities and labels."""
        return await self.get_file(
            file_id,
            fields="id,name,mimeType,size,parents,owners,webViewLink,webContentLink,"
                   "createdTime,modifiedTime,trashed,starred,shared,description,"
                   "version,permissions,capabilities,contentHints,"
                   "imageMediaMetadata,videoMediaMetadata,shortcutDetails",
        )

    async def update_metadata(
        self, file_id: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update file metadata fields (name, description, labels, etc.)."""
        allowed_fields = {"name", "description", "starred", "trashed", "contentHints"}
        body = {k: v for k, v in metadata.items() if k in allowed_fields}
        return self._files.update(
            fileId=file_id,
            body=body,
            fields="id,name,description,starred,modifiedTime",
            supportsAllDrives=True,
        ).execute()

    async def create_shortcut(
        self,
        target_file_id: str,
        name: str,
        parent_folder_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a shortcut to a file."""
        body: Dict[str, Any] = {
            "name": name,
            "mimeType": "application/vnd.google-apps.shortcut",
            "shortcutDetails": {"targetId": target_file_id},
        }
        if parent_folder_id:
            body["parents"] = [parent_folder_id]
        return self._files.create(
            body=body,
            fields="id,name,mimeType,shortcutDetails",
            supportsAllDrives=True,
        ).execute()

    async def list_files_in_trash(self, page_size: int = 100) -> Dict[str, Any]:
        """List all trashed files."""
        return await self.list_files(query="trashed=true", page_size=page_size)

    async def batch_operations(self, operations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple file operations. Each op has 'action' and 'params'."""
        results = []
        for op in operations:
            action = op.get("action", "")
            params = op.get("params", {})
            try:
                if action == "get":
                    result = await self.get_file(params["file_id"])
                elif action == "delete":
                    result = await self.delete_file(params["file_id"])
                elif action == "trash":
                    result = await self.trash_file(params["file_id"])
                elif action == "move":
                    result = await self.move_file(params["file_id"], params["new_parent_id"])
                elif action == "copy":
                    result = await self.copy_file(params["file_id"], params.get("name"), params.get("parent_folder_id"))
                else:
                    result = {"error": f"Unknown batch action: {action}"}
                results.append({"action": action, "status": "OK", "result": result})
            except Exception as e:
                results.append({"action": action, "status": "ERROR", "error": str(e)})
        return results
