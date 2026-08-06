"""BizOS Connector HTTP Retry Utility

Provides `http_request_with_retry()` — a provider-agnostic wrapper that:
  - Performs exponential backoff on HTTP 429 (rate-limit) and 5xx errors
  - Raises structured `ConnectorException` for all terminal failures
  - Detects 401 and raises `ConnectorException(code="AUTH_EXPIRED")` so callers
    can trigger a token refresh and retry
  - Parses provider `Retry-After` header when present

Usage:
    from app.connectors.sdk.retry import http_request_with_retry

    data = http_request_with_retry(
        method="GET",
        url="https://api.hubapi.com/crm/v3/objects/contacts",
        headers={"Authorization": f"Bearer {token}"},
        provider="hubspot",
        action="list_contacts",
    )
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

import structlog

from app.connectors.sdk.errors import ConnectorError, ConnectorException

logger = structlog.get_logger(__name__)

# Default backoff schedule in seconds: 1s, 2s, 4s (exponential), capped at 60s
_DEFAULT_BACKOFF = [1, 2, 4]
_MAX_RETRIES = 3


def http_request_with_retry(
    method: str,
    url: str,
    headers: Dict[str, str],
    payload: Optional[Dict] = None,
    provider: str = "unknown",
    action: str = "api_call",
    timeout: int = 15,
    max_retries: int = _MAX_RETRIES,
) -> Any:
    """Execute an HTTP request with exponential backoff for 429/5xx.

    Returns:
        Parsed JSON response body (dict / list).

    Raises:
        ConnectorException with structured ConnectorError for all failures.
    """
    data = json.dumps(payload).encode() if payload else None
    last_exc: Optional[ConnectorException] = None

    for attempt in range(max_retries + 1):
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read().decode()
                return json.loads(body) if body.strip() else {}

        except urllib.error.HTTPError as exc:
            body = ""
            try:
                body = exc.read().decode()
            except Exception:
                pass

            http_code = exc.code

            # ── 401 / 403: auth failure ──────────────────────────────────────
            if http_code in (401, 403):
                reason = "TOKEN_EXPIRED" if http_code == 401 else "INSUFFICIENT_SCOPE"
                last_exc = ConnectorException(ConnectorError(
                    code="AUTH_EXPIRED",
                    provider=provider,
                    action=action,
                    severity="CRITICAL",
                    retryable=False,
                    user_message=f"Authentication failed for {provider}: {reason}",
                    technical_details={"http_status": http_code, "body": body[:500]},
                ))
                raise last_exc  # non-retryable

            # ── 404: not found ────────────────────────────────────────────────
            if http_code == 404:
                raise ConnectorException(ConnectorError(
                    code="NOT_FOUND",
                    provider=provider,
                    action=action,
                    severity="ERROR",
                    retryable=False,
                    user_message=f"Resource not found in {provider}.",
                    technical_details={"http_status": 404, "body": body[:500]},
                ))

            # ── 409: conflict ─────────────────────────────────────────────────
            if http_code == 409:
                raise ConnectorException(ConnectorError(
                    code="CONFLICT",
                    provider=provider,
                    action=action,
                    severity="ERROR",
                    retryable=False,
                    user_message=f"Conflict in {provider}: duplicate or version mismatch.",
                    technical_details={"http_status": 409, "body": body[:500]},
                ))

            # ── 422: validation ───────────────────────────────────────────────
            if http_code == 422:
                raise ConnectorException(ConnectorError(
                    code="INVALID_PARAMS",
                    provider=provider,
                    action=action,
                    severity="ERROR",
                    retryable=False,
                    user_message=f"{provider} rejected the payload: {body[:200]}",
                    technical_details={"http_status": 422, "body": body[:500]},
                ))

            # ── 429: rate limit — backoff and retry ───────────────────────────
            if http_code == 429:
                retry_after = int(exc.headers.get("Retry-After", _DEFAULT_BACKOFF[min(attempt, len(_DEFAULT_BACKOFF) - 1)]))
                wait = min(retry_after, 60)
                logger.warning(
                    "connector_rate_limited",
                    provider=provider,
                    action=action,
                    attempt=attempt,
                    wait_seconds=wait,
                )
                last_exc = ConnectorException(ConnectorError(
                    code="RATE_LIMITED",
                    provider=provider,
                    action=action,
                    severity="WARNING",
                    retryable=True,
                    user_message=f"{provider} rate limit hit. Backing off {wait}s.",
                    technical_details={"http_status": 429, "retry_after": wait},
                ))
                if attempt < max_retries:
                    time.sleep(wait)
                    continue
                raise last_exc

            # ── 5xx: provider error — exponential backoff ─────────────────────
            if http_code >= 500:
                wait = _DEFAULT_BACKOFF[min(attempt, len(_DEFAULT_BACKOFF) - 1)]
                logger.warning(
                    "connector_server_error",
                    provider=provider,
                    action=action,
                    http_code=http_code,
                    attempt=attempt,
                    wait_seconds=wait,
                )
                last_exc = ConnectorException(ConnectorError(
                    code="PROVIDER_ERROR",
                    provider=provider,
                    action=action,
                    severity="ERROR",
                    retryable=True,
                    user_message=f"{provider} server error {http_code}. Backing off {wait}s.",
                    technical_details={"http_status": http_code, "body": body[:500]},
                ))
                if attempt < max_retries:
                    time.sleep(wait)
                    continue
                raise last_exc

            # ── Other HTTP errors ─────────────────────────────────────────────
            raise ConnectorException(ConnectorError(
                code="HTTP_ERROR",
                provider=provider,
                action=action,
                severity="ERROR",
                retryable=False,
                user_message=f"{provider} returned HTTP {http_code}: {body[:200]}",
                technical_details={"http_status": http_code, "body": body[:500]},
            ))

        except urllib.error.URLError as exc:
            # Network-level error (DNS, connection refused, timeout)
            wait = _DEFAULT_BACKOFF[min(attempt, len(_DEFAULT_BACKOFF) - 1)]
            logger.warning(
                "connector_network_error",
                provider=provider,
                action=action,
                attempt=attempt,
                error=str(exc),
            )
            last_exc = ConnectorException(ConnectorError(
                code="NETWORK_ERROR",
                provider=provider,
                action=action,
                severity="ERROR",
                retryable=True,
                user_message=f"Network error reaching {provider}: {exc.reason}",
                technical_details={"error": str(exc)},
            ))
            if attempt < max_retries:
                time.sleep(wait)
                continue
            raise last_exc

    raise last_exc  # Should never reach here but satisfies type checker
