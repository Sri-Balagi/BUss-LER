import json
from pathlib import Path
from app.sdk.core.app_base import BizOSApp
from app.sdk.manifest.app_manifest import AppManifest

class MyApp(BizOSApp):
    def run(self) -> None:
        print(f"Running {self.manifest.name} v{self.manifest.version}")
        health = self.client.get_health()
        print(f"API Health: {health.success}")

if __name__ == "__main__":
    manifest_path = Path(__file__).parent / "manifest.json"
    with open(manifest_path, "r") as f:
        data = json.load(f)
    
    manifest = AppManifest.model_validate(data)
    app = MyApp(manifest=manifest)
    try:
        app.run()
    finally:
        app.shutdown()
