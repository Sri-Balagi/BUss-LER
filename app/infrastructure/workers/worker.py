import asyncio
import logging
import uuid
import time
from typing import Callable, Any

logger = logging.getLogger("bizos.worker")

class DistributedWorker:
    def __init__(self, queue_name: str, broker: Any):
        self.worker_id = str(uuid.uuid4())
        self.queue_name = queue_name
        self.broker = broker
        self.is_running = False
        self._task = None
        self._handlers = {}

    def register_handler(self, task_type: str, handler: Callable):
        self._handlers[task_type] = handler

    async def start(self):
        self.is_running = True
        logger.info(f"Worker {self.worker_id} starting on queue {self.queue_name}")
        asyncio.create_task(self._heartbeat())
        while self.is_running:
            try:
                msg = await self.broker.pop(self.queue_name, timeout=5)
                if msg:
                    await self._process_message(msg)
            except Exception as e:
                logger.error(f"Worker {self.worker_id} error: {e}")
                await asyncio.sleep(1)

    async def _heartbeat(self):
        while self.is_running:
            await self.broker.heartbeat(self.worker_id, time.time())
            await asyncio.sleep(10)

    async def _process_message(self, msg: dict):
        task_type = msg.get("type")
        handler = self._handlers.get(task_type)
        if handler:
            logger.info(f"Worker {self.worker_id} executing {task_type}")
            try:
                await handler(msg)
                await self.broker.ack(msg["id"])
            except Exception as e:
                logger.error(f"Task failed: {e}")
                await self.broker.nack(msg["id"])

    async def stop(self):
        logger.info(f"Worker {self.worker_id} shutting down gracefully...")
        self.is_running = False
