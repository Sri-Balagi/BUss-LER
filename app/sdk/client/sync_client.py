import httpx
from typing import Any, Dict, List, Optional

from app.sdk.client.config import SDKConfig
from app.sdk.client.models import RegistryItemModel, SDKResponse, ToolExecutionRequest


class BizOSClient:
    """
    Synchronous client for interacting with the BizOS API.
    """

    def __init__(self, config: Optional[SDKConfig] = None):
        self.config = config or SDKConfig()
        self._client = httpx.Client(
            base_url=self.config.base_url,
            headers=self.config.get_auth_headers(),
            timeout=self.config.timeout_seconds,
        )

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _handle_response(self, response: httpx.Response) -> SDKResponse:
        # We assume the API always returns a BizOSResponse-shaped payload on 2xx/4xx
        # In a robust implementation we'd check content types and handle raw 500s.
        try:
            data = response.json()
            return SDKResponse(**data)
        except Exception as e:
            response.raise_for_status()
            raise RuntimeError(f"Unexpected response format: {response.text}") from e

    # ── API Methods ─────────────────────────────────────────────────────────

    def get_health(self) -> SDKResponse:
        """Ping the gateway health check."""
        response = self._client.get("/api/v1/health")
        return self._handle_response(response)

    # ── Registry Commands ───────────────────────────────────────────────────

    def list_registry_items(self, registry_name: str) -> List[RegistryItemModel]:
        """Lists items in a given registry."""
        response = self._client.get(f"/api/v1/registries/{registry_name}/items")
        result = self._handle_response(response)
        if result.success and result.data:
            return [RegistryItemModel(**item) for item in result.data]
        return []

    # ── Execution Commands ──────────────────────────────────────────────────

    def list_active_workflows(self) -> List[Dict[str, Any]]:
        """Lists currently active workflows from the runtime environment."""
        response = self._client.get("/api/v1/workflows")
        result = self._handle_response(response)
        if result.success and result.data:
            return result.data
        return []

    def get_memory_status(self) -> Dict[str, Any]:
        """Retrieves system memory status."""
        response = self._client.get("/api/v1/memory")
        result = self._handle_response(response)
        if result.success and result.data:
            return result.data
        return {"status": "Unknown", "message": "Failed to retrieve memory status"}
