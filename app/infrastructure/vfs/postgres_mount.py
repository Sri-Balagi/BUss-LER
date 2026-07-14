"""
Wave-2 Milestone 4: Storage Layer — Concrete VFS Mounts
=========================================================
PostgresMount: bridges the VFS IVirtualMount contract to Supabase/Postgres.

Design
------
- URI scheme: ``pg://<table>/<row_id>``
- Reads and writes rows as JSON documents via the Supabase REST API.
- The mount is intentionally stateless; connection management is delegated
  to the existing SupabaseService singleton so we never create duplicate pools.
- All I/O is async-compatible; sync wrappers are provided for VFS compatibility.
"""
from __future__ import annotations

import json
from typing import Any

from app.infrastructure.vfs.vfs import IVirtualMount, IVirtualNode


class PostgresNode(IVirtualNode):
    """
    A VFS node backed by a single Postgres row (via Supabase REST).

    path     : ``pg://<table>/<row_id>``
    metadata : Populated at construction time with table / row_id.
    """

    path: str
    metadata: dict

    model_config = {"arbitrary_types_allowed": True}

    def model_post_init(self, __context: Any) -> None:  # noqa: D401
        # Parse path: pg://<table>/<row_id>
        parts = self.path.replace("pg://", "").split("/", 1)
        object.__setattr__(self, "_table", parts[0] if parts else "")
        object.__setattr__(self, "_row_id", parts[1] if len(parts) > 1 else "")
        if not hasattr(self, "_client"):
            object.__setattr__(self, "_client", None)

    def read(self) -> Any:
        """
        Synchronous read – returns the raw row dict from Postgres.
        Callers in async contexts should use ``asyncio.run`` or await a wrapper.
        """
        # In a full production implementation this would call:
        #   response = await self._client.table(self._table).select("*").eq("id", self._row_id).single().execute()
        # For now we return metadata as a placeholder until the async caller
        # layer is wired (Milestone 5+).
        return {
            "path": self.path,
            "table": self._table,
            "row_id": self._row_id,
            "note": "PostgresNode.read() requires async context — use await mount.async_read(uri)",
        }

    def write(self, content: Any) -> None:
        """Synchronous write stub — delegates to async_write in production."""
        # Same limitation as read() above.
        pass


class PostgresMount(IVirtualMount):
    """
    VFS mount backed by Supabase (Postgres).

    Registered under the ``pg://`` scheme in the MountRegistry.
    """

    def __init__(self, supabase_client: Any = None) -> None:
        """
        Parameters
        ----------
        supabase_client:
            An initialised AsyncClient from SupabaseService.get_client().
            May be None during testing/offline use.
        """
        self._client = supabase_client

    @property
    def scheme(self) -> str:
        return "pg"

    def resolve(self, path: str) -> IVirtualNode:
        """
        Resolve a ``pg://`` URI to a PostgresNode.

        Example URI: ``pg://digital_twins/uuid-1234``
        """
        node = PostgresNode(
            path=path,
            metadata={"scheme": "pg", "uri": path},
        )
        object.__setattr__(node, "_client", self._client)
        return node

    async def async_read(self, uri: str) -> Any:
        """
        Truly async read from Postgres via Supabase REST.
        Used by the async application layer.
        """
        parts = uri.replace("pg://", "").split("/", 1)
        table = parts[0]
        row_id = parts[1] if len(parts) > 1 else None

        if self._client is None:
            raise RuntimeError("PostgresMount: no Supabase client configured.")

        query = self._client.table(table).select("*")
        if row_id:
            query = query.eq("id", row_id).single()
        response = await query.execute()
        return response.data

    async def async_write(self, uri: str, content: Any) -> None:
        """Truly async upsert to Postgres via Supabase REST."""
        parts = uri.replace("pg://", "").split("/", 1)
        table = parts[0]

        if self._client is None:
            raise RuntimeError("PostgresMount: no Supabase client configured.")

        await self._client.table(table).upsert(content).execute()
