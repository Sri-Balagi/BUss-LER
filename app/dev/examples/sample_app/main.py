import json
import logging
from pathlib import Path
from app.sdk.core.app_base import BizOSApp
from app.sdk.manifest.app_manifest import AppManifest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DataProcessorApp")

class DataProcessorApp(BizOSApp):
    def run(self) -> None:
        logger.info(f"Starting {self.manifest.name} (v{self.manifest.version})")
        logger.info("Checking connection to BizOS Kernel...")
        health = self.client.get_health()
        if health.success:
            logger.info("Connection established. Kernel is healthy.")
            # Do mock processing
            logger.info("Processing data...")
            logger.info("Finished processing.")
        else:
            logger.error("Failed to connect to Kernel.")

if __name__ == "__main__":
    manifest_path = Path(__file__).parent / "manifest.json"
    with open(manifest_path, "r") as f:
        data = json.load(f)
    
    app = DataProcessorApp(manifest=AppManifest.model_validate(data))
    try:
        app.run()
    finally:
        app.shutdown()
