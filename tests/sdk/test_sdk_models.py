from app.sdk.client.config import SDKConfig
from app.sdk.client.models import SDKResponse, RegistryItemModel

def test_sdk_config():
    config = SDKConfig(base_url="http://test", api_key="secret")
    headers = config.get_auth_headers()
    assert headers["X-API-Key"] == "secret"

def test_sdk_response_model():
    res = SDKResponse(success=True, data={"key": "value"})
    assert res.success is True
    assert res.data["key"] == "value"

def test_registry_item_model():
    item = RegistryItemModel(id="1", name="test", type="tool", metadata={})
    assert item.name == "test"
