import json
import logging
from typing import Any, Dict

from app.sdk.client.config import SDKConfig
from app.sdk.client.sync_client import BizOSClient

logger = logging.getLogger(__name__)


class DevSandbox:
    """
    Ephemeral sandbox environment for testing Apps and Plugins locally.
    Mocks necessary BizOS Kernel services without requiring a full OS boot.
    """

    def __init__(self):
        self.config = SDKConfig(base_url="http://localhost:8000")
        self.client = BizOSClient(config=self.config)
        self.state: Dict[str, Any] = {}

    def start(self) -> None:
        logger.info("Starting DevSandbox...")
        # Mock initialization logic
        self.state["running"] = True

    def stop(self) -> None:
        logger.info("Stopping DevSandbox...")
        self.client.close()
        self.state.clear()
