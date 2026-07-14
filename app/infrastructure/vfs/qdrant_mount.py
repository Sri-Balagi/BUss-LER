"""
Wave-2 Milestone 4: Storage Layer — Concrete VFS Mounts
=========================================================
QdrantMount: bridges the VFS IVirtualMount contract to Qdrant vector store.

Design
------
- URI scheme: ``qdrant://<collection>/<point_id>``
- Reads and writes Qdrant points (vectors + payloads).
- Wraps the existing QdrantService client.
- Async-first; sync read/write stubs provided for VFS interface compliance.
"""
from __future__ import annotations

from typing import Any

from app.infrastructure.vfs.vfs import IVirtualMount, IVirtualNode


class QdrantNode(IVirtualNode):
    """
    A VFS node backed by a single Qdrant point.

    path     : ``qdrant://<collection>/<point_id>``
    metadata : collection name and point_id.
    """

    path: str
    metadata: dict

    model_config = {"arbitrary_types_allowed": True}

    def model_post_init(self, __context: Any) -> None:
        parts = self.path.replace("qdrant://", "").split("/", 1)
        object.__setattr__(self, "_collection", parts[0] if parts else "")
        object.__setattr__(self, "_point_id", parts[1] if len(parts) > 1 else "")
        if not hasattr(self, "_client"):
            object.__setattr__(self, "_client", None)

    def read(self) -> Any:
        """Synchronous read stub. Use async_read for production."""
        return {
            "path": self.path,
            "collection": self._collection,
            "point_id": self._point_id,
            "note": "QdrantNode.read() requires async context — use await mount.async_read(uri)",
        }

    def write(self, content: Any) -> None:
        """Synchronous write stub. Use async_write for production."""
        pass


class QdrantMount(IVirtualMount):
    """
    VFS mount backed by Qdrant.
    Registered under the ``qdrant://`` scheme in the MountRegistry.
    """

    def __init__(self, qdrant_client: Any = None) -> None:
        """
        Parameters
        ----------
        qdrant_client:
            An initialised AsyncQdrantClient from QdrantService.get_client().
            May be None during testing/offline use.
        """
        self._client = qdrant_client

    @property
    def scheme(self) -> str:
        return "qdrant"

    def resolve(self, uri: str) -> IVirtualNode:
        """Resolve a ``qdrant://`` URI to a QdrantNode."""
        node = QdrantNode(
            path=uri,
            metadata={"scheme": "qdrant", "uri": uri},
        )
        object.__setattr__(node, "_client", self._client)
        return node

    async def async_read(self, uri: str) -> Any:
        """
        Fetch a point from Qdrant by point_id.
        Returns the point payload as a dict.
        """
        parts = uri.replace("qdrant://", "").split("/", 1)
        collection = parts[0]
        point_id = parts[1] if len(parts) > 1 else None

        if self._client is None:
            raise RuntimeError("QdrantMount: no Qdrant client configured.")

        results = await self._client.retrieve(
            collection_name=collection,
            ids=[point_id],
            with_payload=True,
            with_vectors=False,
        )
        return results[0].payload if results else None

    async def async_write(self, uri: str, content: dict) -> None:
        """
        Upsert a point into Qdrant.

        content must include:
          - ``vector`` (list[float])
          - ``payload`` (dict)
          - optionally ``id`` (str UUID); falls back to point_id from URI
        """
        from qdrant_client.http.models import PointStruct

        parts = uri.replace("qdrant://", "").split("/", 1)
        collection = parts[0]
        point_id = content.get("id") or (parts[1] if len(parts) > 1 else None)

        if self._client is None:
            raise RuntimeError("QdrantMount: no Qdrant client configured.")

        point = PointStruct(
            id=str(point_id),
            vector=content["vector"],
            payload=content.get("payload", {}),
        )
        await self._client.upsert(collection_name=collection, points=[point])
