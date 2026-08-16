from abc import ABC, abstractmethod

from app.sdk.client.config import SDKConfig
from app.sdk.client.sync_client import BizOSClient
from app.sdk.manifest.app_manifest import AppManifest


class BizOSApp(ABC):
    """
    Base class for creating a standalone BizOS Application.
    Provides lifecycle hooks and an injected SDK client.
    """

    def __init__(self, manifest: AppManifest, config: SDKConfig | None = None):
        self.manifest = manifest
        self.client = BizOSClient(config=config)

    @abstractmethod
    def run(self) -> None:
        """Main entry point for the application."""
        pass

    def shutdown(self) -> None:
        """Cleanup resources."""
        self.client.close()
