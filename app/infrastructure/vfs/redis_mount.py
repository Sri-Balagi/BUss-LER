"""
Wave-2 Milestone 4: Storage Layer — Concrete VFS Mounts
=========================================================
RedisMount: bridges the VFS IVirtualMount contract to Redis key-value store.

Design
------
- URI scheme: ``redis://<key>``
- Reads and writes JSON-serialised values in Redis.
- Uses a lazily-connected Redis client (from env ``REDIS_URL``).
- TTL can be embedded in the URI fragment: ``redis://mykey#ttl=300``
"""
from __future__ import annotations

import json
import os
from typing import Any

from app.infrastructure.vfs.vfs import IVirtualMount, IVirtualNode


class RedisNode(IVirtualNode):
    """
    A VFS node backed by a single Redis key.

    path     : ``redis://<key>`` (optionally ``redis://<key>#ttl=<seconds>``)
    metadata : key name and optional TTL.
    """

    path: str
    metadata: dict

    model_config = {"arbitrary_types_allowed": True}

    def model_post_init(self, __context: Any) -> None:
        # Parse key and TTL from the URI path
        raw = self.path.replace("redis://", "")
        if "#ttl=" in raw:
            key_part, ttl_part = raw.split("#ttl=", 1)
            object.__setattr__(self, "_key", key_part)
            try:
                object.__setattr__(self, "_ttl", int(ttl_part))
            except ValueError:
                object.__setattr__(self, "_ttl", None)
        else:
            object.__setattr__(self, "_key", raw)
            object.__setattr__(self, "_ttl", None)
        # _client is set externally by RedisMount.resolve() after construction
        if not hasattr(self, "_client"):
            object.__setattr__(self, "_client", None)

    def read(self) -> Any:
        """Synchronous read from Redis."""
        if self._client is None:
            return None
        raw = self._client.get(self._key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return raw

    def write(self, content: Any) -> None:
        """Synchronous write to Redis with optional TTL."""
        if self._client is None:
            return
        payload = json.dumps(content)
        if self._ttl:
            self._client.setex(self._key, self._ttl, payload)
        else:
            self._client.set(self._key, payload)


class RedisMount(IVirtualMount):
    """
    VFS mount backed by Redis.
    Registered under the ``redis://`` scheme in the MountRegistry.

    Unlike PostgresMount and QdrantMount, Redis I/O is synchronous so the
    VFS read/write contract is fully satisfied without async wrappers.
    """

    def __init__(self, redis_client: Any = None) -> None:
        """
        Parameters
        ----------
        redis_client:
            An initialised redis.Redis (sync) client.
            If None, a client is created lazily from REDIS_URL.
        """
        self._client = redis_client

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client
        import redis
        url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._client = redis.Redis.from_url(url, decode_responses=True)
        return self._client

    @property
    def scheme(self) -> str:
        return "redis"

    def resolve(self, uri: str) -> IVirtualNode:
        """Resolve a ``redis://`` URI to a RedisNode."""
        node = RedisNode(
            path=uri,
            metadata={"scheme": "redis", "uri": uri},
        )
        # Set _client after construction — Pydantic ignores unknown kwargs.
        object.__setattr__(node, "_client", self._get_client())
        return node
