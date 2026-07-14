"""
Redis-backed distributed System Bus for BizOS.

Design notes
------------
- redis is imported at module level. The package is a required dependency
  for distributed mode (installed via `uv add redis`).
- Uses Redis Pub/Sub for low-latency inter-node event delivery.
- Messages are serialised as JSON; consumers should run listen() in a
  dedicated background thread or process.
"""
from __future__ import annotations

import json
import os
from typing import Any, Generator

import redis  # type: ignore[import]

from app.runtime.distributed.interfaces import IDistributedSystemBus


class RedisSystemBus(IDistributedSystemBus):
    """
    Pub/Sub distributed system bus backed by Redis.

    Connection URL is resolved from the environment variable
    ``REDIS_URL`` (defaults to ``redis://localhost:6379/0``).
    """

    def __init__(self, redis_url: str | None = None) -> None:
        url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._client = redis.Redis.from_url(url, decode_responses=True)
        self._pubsub = self._client.pubsub(ignore_subscribe_messages=True)

    def publish(self, channel: str, message: Any) -> None:
        """Publish a JSON-serialised message to a Redis channel."""
        payload = json.dumps(message)
        self._client.publish(channel, payload)

    def subscribe(self, channel: str) -> None:
        """Subscribe to a Redis channel."""
        self._pubsub.subscribe(channel)

    def listen(self) -> Generator[Any, None, None]:
        """
        Blocking generator that yields deserialised messages from subscribed channels.
        Run this in a dedicated thread or background coroutine.
        """
        for raw in self._pubsub.listen():
            if raw and raw.get("type") == "message":
                try:
                    yield json.loads(raw["data"])
                except (json.JSONDecodeError, KeyError):
                    yield raw.get("data")
