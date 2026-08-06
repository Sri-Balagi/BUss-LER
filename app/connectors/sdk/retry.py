import httpx
import json
import time
from typing import Dict, Any, Optional
from app.connectors.sdk.errors import ConnectorException

def http_request_with_retry(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    json_data: Optional[Any] = None,
    data: Optional[Any] = None,
    params: Optional[Dict[str, Any]] = None,
    max_retries: int = 3
) -> httpx.Response:
    last_err = None
    for attempt in range(max_retries):
        try:
            # We use a synchronous client here as a simple mock/poly-fill for the removed SDK module
            with httpx.Client() as client:
                resp = client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json_data,
                    data=data,
                    params=params,
                    timeout=30.0
                )
                if resp.status_code == 429 or resp.status_code >= 500:
                    time.sleep(2 ** attempt)
                    continue
                return resp
        except Exception as e:
            last_err = e
            time.sleep(2 ** attempt)
            
    raise ConnectorException(f"HTTP request failed after {max_retries} attempts: {str(last_err)}")
