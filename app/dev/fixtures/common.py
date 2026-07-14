from app.sdk.manifest.app_manifest import AppManifest

def get_dummy_manifest() -> AppManifest:
    return AppManifest(
        name="dummy_app",
        version="1.0.0",
        description="A dummy app for testing",
        author="test",
        dependencies=[],
        permissions=["fs:read"]
    )
