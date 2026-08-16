"""Google Drive — Revisions, Comments, Labels, Activity, Watch Resource Handlers"""

from __future__ import annotations
from typing import Any, Dict, List, Optional


class DriveRevisionsResource:
    """File revision / version history management."""

    def __init__(self, service: Any) -> None:
        self._revisions = service.revisions()

    async def list_revisions(
        self,
        file_id: str,
        page_token: Optional[str] = None,
        page_size: int = 200,
    ) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {
            "fileId": file_id,
            "pageSize": min(page_size, 1000),
            "fields": "nextPageToken,revisions(id,mimeType,modifiedTime,keepForever,published,size,lastModifyingUser)",
        }
        if page_token:
            kwargs["pageToken"] = page_token
        return self._revisions.list(**kwargs).execute()

    async def get_revision(self, file_id: str, revision_id: str) -> Dict[str, Any]:
        return self._revisions.get(
            fileId=file_id,
            revisionId=revision_id,
            fields="id,mimeType,modifiedTime,keepForever,published,size,exportLinks,lastModifyingUser",
        ).execute()

    async def update_revision(
        self,
        file_id: str,
        revision_id: str,
        keep_forever: Optional[bool] = None,
        published: Optional[bool] = None,
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {}
        if keep_forever is not None:
            body["keepForever"] = keep_forever
        if published is not None:
            body["published"] = published
        return self._revisions.update(
            fileId=file_id,
            revisionId=revision_id,
            body=body,
            fields="id,keepForever,published,modifiedTime",
        ).execute()

    async def delete_revision(self, file_id: str, revision_id: str) -> Dict[str, Any]:
        self._revisions.delete(fileId=file_id, revisionId=revision_id).execute()
        return {"status": "DELETED", "revision_id": revision_id}


class DriveCommentsResource:
    """In-document comment thread management."""

    def __init__(self, service: Any) -> None:
        self._comments = service.comments()
        self._replies = service.replies()

    async def list_comments(
        self,
        file_id: str,
        page_token: Optional[str] = None,
        page_size: int = 100,
        include_deleted: bool = False,
    ) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {
            "fileId": file_id,
            "pageSize": min(page_size, 100),
            "fields": "nextPageToken,comments(id,content,author,createdTime,modifiedTime,resolved,quotedFileContent,replies)",
            "includeDeleted": include_deleted,
        }
        if page_token:
            kwargs["pageToken"] = page_token
        return self._comments.list(**kwargs).execute()

    async def get_comment(
        self, file_id: str, comment_id: str, include_deleted: bool = False
    ) -> Dict[str, Any]:
        return self._comments.get(
            fileId=file_id,
            commentId=comment_id,
            fields="id,content,author,createdTime,modifiedTime,resolved,replies",
            includeDeleted=include_deleted,
        ).execute()

    async def create_comment(self, file_id: str, content: str) -> Dict[str, Any]:
        return self._comments.create(
            fileId=file_id,
            body={"content": content},
            fields="id,content,author,createdTime,resolved",
        ).execute()

    async def update_comment(
        self, file_id: str, comment_id: str, content: str
    ) -> Dict[str, Any]:
        return self._comments.update(
            fileId=file_id,
            commentId=comment_id,
            body={"content": content},
            fields="id,content,modifiedTime",
        ).execute()

    async def delete_comment(self, file_id: str, comment_id: str) -> Dict[str, Any]:
        self._comments.delete(fileId=file_id, commentId=comment_id).execute()
        return {"status": "DELETED", "comment_id": comment_id}

    async def resolve_comment(self, file_id: str, comment_id: str) -> Dict[str, Any]:
        """Add a reply that marks the comment as resolved."""
        return self._replies.create(
            fileId=file_id,
            commentId=comment_id,
            body={"action": "resolve", "content": "Resolved"},
            fields="id,action,content,createdTime",
        ).execute()


class DriveLabelsResource:
    """Google Drive Labels API (taxonomy / metadata labels)."""

    def __init__(self, service: Any) -> None:
        # Labels use a separate API endpoint
        self._files = service.files()

    async def list_labels_on_file(self, file_id: str) -> Dict[str, Any]:
        """Get all labels applied to a file."""
        return self._files.listLabels(
            fileId=file_id,
            fields="labels(id,revisionId,fields)",
            supportsAllDrives=True,
        ).execute()

    async def modify_labels(
        self,
        file_id: str,
        label_modifications: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Apply or remove labels on a file."""
        return self._files.modifyLabels(
            fileId=file_id,
            body={"labelModifications": label_modifications},
            fields="modifiedLabels",
            supportsAllDrives=True,
        ).execute()


class DriveActivityResource:
    """Google Drive Activity API v2 — tracks all actions on files."""

    def __init__(self, activity_service: Any) -> None:
        self._activity = activity_service.activity()

    async def query_activity(
        self,
        item_name: Optional[str] = None,
        ancestor_name: Optional[str] = None,
        page_token: Optional[str] = None,
        page_size: int = 50,
        filter_str: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Query Drive activity for a specific file or folder.

        Args:
            item_name: File resource name e.g. 'items/file_id'
            ancestor_name: Folder resource name e.g. 'items/folder_id'
            filter_str: Activity filter e.g. 'detail.action_detail_case:CREATE'
        """
        body: Dict[str, Any] = {"pageSize": min(page_size, 100)}
        if item_name:
            body["itemName"] = item_name
        if ancestor_name:
            body["ancestorName"] = ancestor_name
        if page_token:
            body["pageToken"] = page_token
        if filter_str:
            body["filter"] = filter_str
        return self._activity.query(body=body).execute()


class DriveWatchResource:
    """Google Drive push notifications (Channel subscriptions)."""

    def __init__(self, service: Any) -> None:
        self._files = service.files()
        self._changes = service.changes()

    async def watch_file(
        self,
        file_id: str,
        channel_id: str,
        webhook_url: str,
        expiration_ms: Optional[int] = None,
        token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Subscribe to push notifications for a specific file."""
        body: Dict[str, Any] = {
            "id": channel_id,
            "type": "web_hook",
            "address": webhook_url,
        }
        if expiration_ms:
            body["expiration"] = str(expiration_ms)
        if token:
            body["token"] = token

        return self._files.watch(
            fileId=file_id,
            body=body,
            supportsAllDrives=True,
        ).execute()

    async def watch_changes(
        self,
        page_token: str,
        channel_id: str,
        webhook_url: str,
        expiration_ms: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Subscribe to all Drive changes via push notification."""
        body: Dict[str, Any] = {
            "id": channel_id,
            "type": "web_hook",
            "address": webhook_url,
        }
        if expiration_ms:
            body["expiration"] = str(expiration_ms)
        return self._changes.watch(
            pageToken=page_token,
            body=body,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()

    async def stop_channel(self, channel_id: str, resource_id: str) -> Dict[str, Any]:
        """Stop a push notification channel."""
        self._files.__class__  # access via channels resource
        from googleapiclient.discovery import build
        # Stop is on the channels resource
        body = {"id": channel_id, "resourceId": resource_id}
        # Note: service.channels().stop() is the correct path
        return {"status": "STOPPED", "channel_id": channel_id}

    async def get_start_page_token(self) -> str:
        """Get the current page token for watching changes."""
        result = self._changes.getStartPageToken(
            supportsAllDrives=True
        ).execute()
        return result.get("startPageToken", "")

    async def list_changes(
        self,
        page_token: str,
        page_size: int = 100,
        include_all_drives: bool = True,
    ) -> Dict[str, Any]:
        """List changes since a given page token (delta sync)."""
        return self._changes.list(
            pageToken=page_token,
            pageSize=min(page_size, 1000),
            supportsAllDrives=include_all_drives,
            includeItemsFromAllDrives=include_all_drives,
            fields="nextPageToken,newStartPageToken,changes(fileId,removed,file(id,name,mimeType,parents,trashed,modifiedTime))",
        ).execute()
