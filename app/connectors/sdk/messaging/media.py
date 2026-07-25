"""Media handling framework for messaging SDK."""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel
from app.connectors.canonical.messaging import CanonicalAttachment


class MediaUploader:
    """Helper service for uploading media attachments to communication channels."""

    async def upload(
        self,
        connector_id: str,
        file_bytes: bytes,
        filename: str,
        mime_type: str,
    ) -> CanonicalAttachment:
        return CanonicalAttachment(
            source_connector=connector_id,
            source_id="media_mock_123",
            file_name=filename,
            mime_type=mime_type,
            file_size_bytes=len(file_bytes),
            url=f"https://storage.bizos.ai/media/{filename}",
        )


class MediaDownloader:
    """Helper service for downloading media attachments from communication channels."""

    async def download(self, media_url: str) -> bytes:
        return b"mock_media_binary_data"
