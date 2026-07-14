import httpx
from typing import Any, Dict, List, Optional

from app.sdk.client.config import SDKConfig
from app.sdk.client.models import RegistryItemModel, SDKResponse, ToolExecutionRequest


class AsyncBizOSClient:
    """
    Asynchronous client for interacting with the BizOS API.
    """

    def __init__(self, config: Optional[SDKConfig] = None):
        self.config = config or SDKConfig()
        self._client = httpx.AsyncClient(
            base_url=self.config.base_url,
            headers=self.config.get_auth_headers(),
            timeout=self.config.timeout_seconds,
        )

    async def close(self):
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def _handle_response(self, response: httpx.Response) -> SDKResponse:
        try:
            data = response.json()
            return SDKResponse(**data)
        except Exception as e:
            response.raise_for_status()
            raise RuntimeError(f"Unexpected response format: {response.text}") from e

    # ── API Methods ─────────────────────────────────────────────────────────

    async def get_health(self) -> SDKResponse:
        response = await self._client.get("/api/v1/health")
        return self._handle_response(response)

    async def list_registry_items(self, registry_name: str) -> List[RegistryItemModel]:
        response = await self._client.get(f"/api/v1/registries/{registry_name}/items")
        result = self._handle_response(response)
        if result.success and result.data:
            return [RegistryItemModel(**item) for item in result.data]
        return []

    async def list_active_workflows(self) -> List[Dict[str, Any]]:
        response = await self._client.get("/api/v1/workflows")
        result = self._handle_response(response)
        if result.success and result.data:
            return result.data
        return []

    async def get_memory_status(self) -> Dict[str, Any]:
        response = await self._client.get("/api/v1/memory")
        result = self._handle_response(response)
        if result.success and result.data:
            return result.data
        return {"status": "Unknown", "message": "Failed to retrieve memory status"}
