"""Microsoft Graph API client — shared across Outlook and Teams connectors.

Provides a thin, retry-aware HTTP client for Microsoft Graph REST API calls.
All connectors import from here instead of duplicating urllib boilerplate.
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional

import structlog

logger = structlog.get_logger(__name__)

GRAPH_BASE = "https://graph.microsoft.com/v1.0"


class GraphAPIError(Exception):
    """Raised on non-2xx responses from Microsoft Graph."""
    def __init__(self, message: str, status_code: int = 0, error_code: str = ""):
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code


def _build_headers(token: str, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if extra:
        headers.update(extra)
    return headers


def graph_request(
    token: str,
    path: str,
    method: str = "GET",
    payload: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, str]] = None,
    retries: int = 3,
    timeout: int = 20,
    extra_headers: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Executes a synchronous Microsoft Graph API request with retry logic.

    Args:
        token: Bearer access token.
        path: Graph API path starting with '/', e.g. '/me/messages'.
        method: HTTP method (GET, POST, PATCH, DELETE).
        payload: JSON body for POST/PATCH requests.
        params: Query string parameters.
        retries: Number of retries on transient errors (429, 503).
        timeout: Request timeout in seconds.
        extra_headers: Any additional headers (e.g. Prefer, Content-Range).

    Returns:
        Parsed JSON response dict. Empty dict for 204 No Content.

    Raises:
        GraphAPIError: On non-retriable API errors.
    """
    url = f"{GRAPH_BASE}{path}"
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"

    headers = _build_headers(token, extra_headers)
    body = json.dumps(payload).encode("utf-8") if payload is not None else None

    for attempt in range(1, retries + 1):
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8")
                if not raw:
                    return {}
                return json.loads(raw)

        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8") if exc.fp else "{}"
            try:
                error_json = json.loads(error_body)
                error_code = error_json.get("error", {}).get("code", "")
                error_msg = error_json.get("error", {}).get("message", error_body)
            except Exception:
                error_code = ""
                error_msg = error_body

            if exc.code == 429:
                retry_after = int(exc.headers.get("Retry-After", 5))
                logger.warning(
                    "Graph API rate limited (429), backing off",
                    path=path,
                    retry_after=retry_after,
                    attempt=attempt,
                )
                if attempt < retries:
                    time.sleep(retry_after)
                    continue

            if exc.code == 503:
                logger.warning("Graph API service unavailable (503)", path=path, attempt=attempt)
                if attempt < retries:
                    time.sleep(2 ** attempt)
                    continue

            logger.error(
                "Graph API HTTP error",
                path=path,
                status=exc.code,
                error_code=error_code,
                error_msg=error_msg,
            )
            raise GraphAPIError(
                f"Microsoft Graph {exc.code} on {path}: {error_msg}",
                status_code=exc.code,
                error_code=error_code,
            ) from exc

        except Exception as exc:
            logger.error("Graph API request error", path=path, error=str(exc), attempt=attempt)
            if attempt < retries:
                time.sleep(2 ** attempt)
                continue
            raise

    raise GraphAPIError(f"Microsoft Graph request failed after {retries} attempts: {path}")


def graph_paginated(
    token: str,
    path: str,
    params: Optional[Dict[str, str]] = None,
    max_pages: int = 10,
) -> list:
    """
    Follows @odata.nextLink pagination and returns a flat list of 'value' items.

    Args:
        token: Bearer access token.
        path: Graph API path starting with '/'.
        params: Initial query parameters.
        max_pages: Safety cap to avoid infinite loops.

    Returns:
        Flat list of all items across pages.
    """
    results = []
    url = f"{GRAPH_BASE}{path}"
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"

    pages = 0
    while url and pages < max_pages:
        # Extract path+query from full URL for graph_request
        parsed = urllib.parse.urlparse(url)
        clean_path = parsed.path.replace("/v1.0", "") or "/"
        clean_params = dict(urllib.parse.parse_qsl(parsed.query)) if parsed.query else None
        data = graph_request(token, clean_path, params=clean_params)
        results.extend(data.get("value", []))
        url = data.get("@odata.nextLink")
        pages += 1

    return results
