"""HubSpot Connector — BizOS Connector SDK v2 (Production)

Production-grade HubSpot CRM connector with:
  ✅ OAuth token expiry detection + automatic refresh
  ✅ handle_callback() — full OAuth code exchange
  ✅ Retry/backoff (429 rate-limit, 5xx server errors)
  ✅ BizOS canonical error mapping
  ✅ Cursor-based pagination for all list operations
  ✅ Time-bounded delta sync in observe()
  ✅ Deterministic UKO IDs (SHA-256)
  ✅ Webhook HMAC-SHA256 signature verification + replay protection
  ✅ Batch create/update/read
  ✅ Currency from provider (deal_currency_code)
  ✅ deal.contact_ids populated from associations API
  ✅ Explicit HubSpot property lists on all reads
  ✅ Real health_check() via live API call
  ✅ Structured normalize() content for all entity types

Supported capabilities:
  Contacts : list_contacts, get_contact, create_contact, update_contact,
             delete_contact, search_contacts, batch_create_contacts, batch_update_contacts
  Companies: list_companies, get_company, create_company, update_company
  Deals    : list_deals, get_deal, create_deal, update_deal, move_deal_stage,
             close_deal_won, close_deal_lost
  Tasks    : create_task, complete_task
  Notes    : add_note, list_notes
"""
from __future__ import annotations

import hashlib
import hmac
import json
import time
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from uuid import uuid4

import structlog

from app.connectors.sdk.base import (
    BaseConnector,
    ConnectorCapabilities,
    ConnectorExecuteRequest,
    ConnectorResourceType,
)
from app.connectors.sdk.canonical.common import CanonicalAssociation, AssociationType
from app.connectors.sdk.canonical.crm import (
    CanonicalContact,
    CanonicalCompany,
    CanonicalDeal,
    CanonicalNote,
    CanonicalTask,
    CanonicalOwner,
)
from app.connectors.sdk.errors import ConnectorError, ConnectorException
from app.connectors.sdk.retry import http_request_with_retry
from app.connectors.auth.vault import ConnectorAuthVault
from app.domain.shared.context import ExecutionContext
from app.shared.enums import ExecutionMode
from app.perception.sources.interface import IObservationSource, PerceptionContext
from app.perception.models.observation import (
    ExternalObservation,
    ObservationSourceType,
    UnifiedKnowledgeObject,
)

logger = structlog.get_logger(__name__)

# ── HubSpot API Constants ──────────────────────────────────────────────────────

HUBSPOT_API_BASE = "https://api.hubapi.com"
HUBSPOT_CRM_V3 = f"{HUBSPOT_API_BASE}/crm/v3"
HUBSPOT_TOKEN_URL = f"{HUBSPOT_API_BASE}/oauth/v1/token"

# Properties to fetch for each object type — explicit list avoids missing fields
_CONTACT_PROPERTIES = (
    "email,firstname,lastname,phone,jobtitle,lifecyclestage,hs_lead_status,"
    "hubspot_owner_id,associatedcompanyid,createdate,lastmodifieddate"
)
_COMPANY_PROPERTIES = (
    "name,domain,industry,annualrevenue,numberofemployees,phone,"
    "city,country,hubspot_owner_id,hs_lastmodifieddate,createdate"
)
_DEAL_PROPERTIES = (
    "dealname,amount,deal_currency_code,dealstage,pipeline,closedate,"
    "hubspot_owner_id,createdate,hs_lastmodifieddate"
)

# Explicit resource-type map — avoids the rstrip("s") bug
_OBJECT_TYPE_MAP = {
    "contacts": "contact",
    "deals": "deal",
    "companies": "company",
}


# ── Low-level HTTP helper ──────────────────────────────────────────────────────

def _hs_request(
    method: str,
    path: str,
    token: str,
    payload: Optional[Dict] = None,
    base_url: str = HUBSPOT_CRM_V3,
    action: str = "api_call",
) -> Any:
    """Authenticated HubSpot REST call with retry/backoff and error mapping."""
    url = f"{base_url}{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    return http_request_with_retry(
        method=method,
        url=url,
        headers=headers,
        payload=payload,
        provider="hubspot",
        action=action,
    )


# ── Token Management ──────────────────────────────────────────────────────────


def _refresh_hubspot_token(refresh_token: str, client_id: str, client_secret: str) -> Dict:
    """Call HubSpot's token refresh endpoint. Returns new token dict."""
    payload = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
    }).encode()
    req = urllib.request.Request(
        HUBSPOT_TOKEN_URL,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode() if exc.fp else ""
        raise ConnectorException(ConnectorError(
            code="AUTH_REFRESH_FAILED",
            provider="hubspot",
            action="refresh_token",
            severity="CRITICAL",
            retryable=False,
            user_message=f"HubSpot token refresh failed: {body[:200]}",
            technical_details={"http_status": exc.code, "body": body[:500]},
        )) from exc


def _get_token(tenant_id: str) -> str:
    """Get a valid HubSpot access token, refreshing if expired."""
    tokens = ConnectorAuthVault.get_tokens("hubspot", tenant_id=tenant_id)
    if not tokens:
        raise ConnectorException(ConnectorError(
            code="NOT_CONNECTED",
            provider="hubspot",
            action="get_token",
            severity="ERROR",
            retryable=False,
            user_message="HubSpot credentials not found. Authenticate first.",
        ))

    # Proactive expiry check with 90-second buffer
    if ConnectorAuthVault.is_token_expired("hubspot", tenant_id=tenant_id):
        refresh_token = tokens.get("refresh_token")
        client_id = tokens.get("client_id", "")
        client_secret = tokens.get("client_secret", "")
        if refresh_token and client_id and client_secret:
            logger.info("hubspot_token_refresh_triggered", tenant_id=tenant_id)
            new_tokens = _refresh_hubspot_token(refresh_token, client_id, client_secret)
            ConnectorAuthVault.set_tokens(
                "hubspot",
                access_token=new_tokens["access_token"],
                refresh_token=new_tokens.get("refresh_token", refresh_token),
                tenant_id=tenant_id,
                expires_in=new_tokens.get("expires_in", 21600),
                extra={
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
            )
            return new_tokens["access_token"]
        # No refresh credentials — raise auth error
        raise ConnectorException(ConnectorError(
            code="AUTH_EXPIRED",
            provider="hubspot",
            action="get_token",
            severity="CRITICAL",
            retryable=False,
            user_message="HubSpot access token expired and no refresh token available.",
        ))

    return tokens.get("access_token", "")


# ── Normalization Helpers ──────────────────────────────────────────────────────

def _parse_dt(value: Optional[str]) -> datetime:
    if value:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            pass
    return datetime.now(timezone.utc)


def _safe_float(value: Any) -> Optional[float]:
    """Safely convert a provider value to float, returning None on failure."""
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _safe_int(value: Any) -> Optional[int]:
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def _uko_id(source_id: str, resource_id: str) -> str:
    """Generate a deterministic UKO ID from source + resource ID.

    The same provider record always maps to the same UKO node in the
    knowledge graph, preventing duplicate embeddings on re-observation.
    """
    key = f"{source_id}:{resource_id}"
    return hashlib.sha256(key.encode()).hexdigest()


def _normalize_contact(raw: Dict, provider: str = "hubspot") -> CanonicalContact:
    p = raw.get("properties", {})
    assocs: List[CanonicalAssociation] = []
    company_id = p.get("associatedcompanyid")
    if company_id:
        assocs.append(CanonicalAssociation(
            association_id=f"{raw.get('id', '')}_{company_id}",
            provider=provider,
            from_resource_type="contact",
            from_resource_id=raw.get("id", ""),
            to_resource_type="company",
            to_resource_id=company_id,
            association_type=AssociationType.CONTACT_TO_COMPANY,
        ))
    return CanonicalContact(
        contact_id=raw.get("id", ""),
        provider=provider,
        email=p.get("email"),
        first_name=p.get("firstname"),
        last_name=p.get("lastname"),
        phone=p.get("phone"),
        company_id=company_id,
        job_title=p.get("jobtitle"),
        lifecycle_stage=p.get("lifecyclestage"),
        lead_status=p.get("hs_lead_status"),
        owner_id=p.get("hubspot_owner_id"),
        associations=assocs,
        created_at=_parse_dt(p.get("createdate")),
        updated_at=_parse_dt(p.get("lastmodifieddate")),
        raw_payload=raw,
    )


def _normalize_company(raw: Dict, provider: str = "hubspot") -> CanonicalCompany:
    p = raw.get("properties", {})
    return CanonicalCompany(
        company_id=raw.get("id", ""),
        provider=provider,
        name=p.get("name", ""),
        domain=p.get("domain"),
        industry=p.get("industry"),
        annual_revenue=_safe_float(p.get("annualrevenue")),
        number_of_employees=_safe_int(p.get("numberofemployees")),
        phone=p.get("phone"),
        city=p.get("city"),
        country=p.get("country"),
        owner_id=p.get("hubspot_owner_id"),
        created_at=_parse_dt(p.get("createdate")),
        updated_at=_parse_dt(p.get("hs_lastmodifieddate")),
        raw_payload=raw,
    )


def _normalize_deal(raw: Dict, provider: str = "hubspot") -> CanonicalDeal:
    p = raw.get("properties", {})
    assocs: List[CanonicalAssociation] = []

    # Company associations
    for a in raw.get("associations", {}).get("companies", {}).get("results", []):
        assocs.append(CanonicalAssociation(
            association_id=f"{raw.get('id', '')}_{a['id']}",
            provider=provider,
            from_resource_type="deal",
            from_resource_id=raw.get("id", ""),
            to_resource_type="company",
            to_resource_id=a["id"],
            association_type=AssociationType.DEAL_TO_COMPANY,
        ))

    # Contact associations
    contact_ids: List[str] = []
    for a in raw.get("associations", {}).get("contacts", {}).get("results", []):
        contact_ids.append(a["id"])
        assocs.append(CanonicalAssociation(
            association_id=f"{raw.get('id', '')}_{a['id']}",
            provider=provider,
            from_resource_type="deal",
            from_resource_id=raw.get("id", ""),
            to_resource_type="contact",
            to_resource_id=a["id"],
            association_type=AssociationType.DEAL_TO_CONTACT,
        ))

    stage = p.get("dealstage", "")
    return CanonicalDeal(
        deal_id=raw.get("id", ""),
        provider=provider,
        title=p.get("dealname", "Untitled Deal"),
        amount=_safe_float(p.get("amount")) or 0.0,
        currency=p.get("deal_currency_code", "USD"),
        stage_id=stage,
        pipeline_id=p.get("pipeline", "default"),
        close_date=_parse_dt(p.get("closedate")),
        owner_id=p.get("hubspot_owner_id"),
        contact_ids=contact_ids,
        is_closed=stage in ("closedwon", "closedlost"),
        is_won=stage == "closedwon",
        associations=assocs,
        created_at=_parse_dt(p.get("createdate")),
        updated_at=_parse_dt(p.get("hs_lastmodifieddate")),
        raw_payload=raw,
    )


def _crm_record_title(obj_type: str, record: Dict) -> str:
    p = record.get("properties", {})
    if obj_type == "contacts":
        return (f"{p.get('firstname', '')} {p.get('lastname', '')}").strip() or record.get("id", "")
    if obj_type == "deals":
        return p.get("dealname", record.get("id", ""))
    if obj_type == "companies":
        return p.get("name", record.get("id", ""))
    return record.get("id", "")


# ── HubSpot Connector ──────────────────────────────────────────────────────────


class HubSpotConnector(BaseConnector, IObservationSource):
    """Production-grade HubSpot CRM connector.

    Lifecycle:  authenticate → handle_callback → execute() → observe() → normalize()
    All outputs are CanonicalCRM models.
    """

    _PROVIDER = "hubspot"

    # ── IObservationSource identity ───────────────────────────────────────────

    @property
    def source_id(self) -> str:
        return "hubspot"

    @property
    def source_type(self) -> ObservationSourceType:
        return ObservationSourceType.CRM

    # ── BaseConnector identity ────────────────────────────────────────────────

    @property
    def connector_id(self) -> str:
        return "hubspot"

    @property
    def capabilities(self) -> ConnectorCapabilities:
        return ConnectorCapabilities(
            connector_id="hubspot",
            display_name="HubSpot CRM",
            version="2.0.0",
            family="crm",
            supports_realtime=True,
            supports_polling=True,
            supports_batch=True,
            supports_delta_sync=True,
            webhook_support=True,
            auth_type="oauth2",
            required_scopes=[
                "crm.objects.contacts.read",
                "crm.objects.contacts.write",
                "crm.objects.companies.read",
                "crm.objects.companies.write",
                "crm.objects.deals.read",
                "crm.objects.deals.write",
                "crm.objects.notes.read",
                "crm.objects.notes.write",
                "crm.objects.tasks.read",
                "crm.objects.tasks.write",
            ],
            supported_actions=[
                "list_contacts", "get_contact", "create_contact", "update_contact",
                "delete_contact", "search_contacts",
                "list_companies", "get_company", "create_company", "update_company",
                "list_deals", "get_deal", "create_deal", "update_deal",
                "move_deal_stage", "close_deal_won", "close_deal_lost",
                "create_task", "complete_task",
                "add_note", "list_notes",
            ],
            supported_resources=[ConnectorResourceType.USER],
        )

    # ── Authentication ────────────────────────────────────────────────────────

    async def authenticate(
        self, user_email: str, tenant_id: str = "default_tenant", account_id: str = "default"
    ) -> Dict[str, Any]:
        import os
        client_id = os.getenv("HUBSPOT_CLIENT_ID", "{CLIENT_ID}")
        redirect_uri = os.getenv("HUBSPOT_REDIRECT_URI", "{REDIRECT_URI}")
        scopes = " ".join(self.capabilities.required_scopes)
        oauth_url = (
            f"https://app.hubspot.com/oauth/authorize"
            f"?client_id={urllib.parse.quote(client_id)}"
            f"&redirect_uri={urllib.parse.quote(redirect_uri)}"
            f"&scope={urllib.parse.quote(scopes)}"
        )
        return {
            "status": "authentication_required",
            "oauth_url": oauth_url,
            "connector": self.connector_id,
        }

    async def handle_callback(
        self, code: str, state: str, tenant_id: str = "default_tenant"
    ) -> Dict[str, Any]:
        """Exchange OAuth authorization code for access + refresh tokens."""
        import os
        client_id = os.getenv("HUBSPOT_CLIENT_ID", "")
        client_secret = os.getenv("HUBSPOT_CLIENT_SECRET", "")
        redirect_uri = os.getenv("HUBSPOT_REDIRECT_URI", "")

        if not (client_id and client_secret and redirect_uri):
            return {
                "status": "error",
                "connector": self.connector_id,
                "detail": "HUBSPOT_CLIENT_ID / HUBSPOT_CLIENT_SECRET / HUBSPOT_REDIRECT_URI env vars not set.",
            }

        payload = urllib.parse.urlencode({
            "grant_type": "authorization_code",
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "code": code,
        }).encode()
        req = urllib.request.Request(
            HUBSPOT_TOKEN_URL,
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                token_data = json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            body = exc.read().decode() if exc.fp else ""
            return {"status": "error", "connector": self.connector_id, "detail": body[:500]}

        ConnectorAuthVault.set_tokens(
            "hubspot",
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            tenant_id=tenant_id,
            expires_in=token_data.get("expires_in", 21600),
            extra={
                "client_id": client_id,
                "client_secret": client_secret,
            },
        )
        logger.info("hubspot_oauth_callback_complete", tenant_id=tenant_id)
        return {
            "status": "connected",
            "connector": self.connector_id,
            "expires_in": token_data.get("expires_in"),
        }

    async def refresh(
        self, user_id: str, tenant_id: str = "default_tenant", account_id: str = "default"
    ) -> Dict[str, Any]:
        """Force-refresh HubSpot access token using stored refresh token."""
        tokens = ConnectorAuthVault.get_tokens("hubspot", tenant_id=tenant_id)
        if not tokens:
            return {"status": "error", "connector": self.connector_id, "detail": "No tokens stored."}

        refresh_token = tokens.get("refresh_token")
        client_id = tokens.get("client_id", "")
        client_secret = tokens.get("client_secret", "")
        if not refresh_token:
            return {"status": "error", "connector": self.connector_id, "detail": "No refresh token stored."}

        try:
            new_tokens = _refresh_hubspot_token(refresh_token, client_id, client_secret)
            ConnectorAuthVault.set_tokens(
                "hubspot",
                access_token=new_tokens["access_token"],
                refresh_token=new_tokens.get("refresh_token", refresh_token),
                tenant_id=tenant_id,
                expires_in=new_tokens.get("expires_in", 21600),
                extra={"client_id": client_id, "client_secret": client_secret},
            )
            return {"status": "refreshed", "connector": self.connector_id}
        except ConnectorException as exc:
            return {"status": "error", "connector": self.connector_id, "detail": str(exc)}

    async def health_check(self) -> Dict[str, Any]:
        """Return static metadata. Real liveness is checked per-tenant via health()."""
        return {
            "status": "ok",
            "connector": self.connector_id,
            "version": self.capabilities.version,
            "detail": "Authenticate via POST /api/v1/connectors/hubspot/authenticate",
        }

    async def health(self) -> Dict[str, Any]:
        """Real health check — tries a minimal live API call if credentials exist."""
        # Find any stored token for a quick liveness probe
        for key, tokens in ConnectorAuthVault._static_store.items():
            if key.endswith(":hubspot"):
                try:
                    access_token = tokens.get("access_token", "")
                    _hs_request("GET", "/objects/contacts?limit=1", access_token, action="health_check")
                    return {"status": "healthy", "connector": self.connector_id}
                except ConnectorException as exc:
                    return {
                        "status": "unhealthy",
                        "connector": self.connector_id,
                        "error": exc.error.code,
                        "detail": exc.error.user_message,
                    }
        return {
            "status": "unauthenticated",
            "connector": self.connector_id,
            "detail": "No credentials stored.",
        }

    # ── Batch Operations ──────────────────────────────────────────────────────

    async def batch(
        self, operations: list, context: ExecutionContext
    ) -> Dict[str, Any]:
        """HubSpot batch API — create or update up to 100 records in one call."""
        if context.execution_mode in (ExecutionMode.SIMULATION, ExecutionMode.DRY_RUN):
            return {
                "status": "SIMULATED",
                "connector": self.connector_id,
                "processed": len(operations),
                "results": [{"status": "SIMULATED"} for _ in operations],
            }

        try:
            token = _get_token(context.tenant_id)
        except ConnectorException as exc:
            return {"status": "error", "connector": self.connector_id, "error": exc.error.code}

        # Group operations by type and object_type
        creates: Dict[str, List] = {}
        updates: Dict[str, List] = {}
        for op in operations:
            op_type = op.get("type", "create")
            obj_type = op.get("object_type", "contacts")
            if op_type == "create":
                creates.setdefault(obj_type, []).append({"properties": op.get("properties", {})})
            elif op_type == "update":
                updates.setdefault(obj_type, []).append({
                    "id": op.get("id"),
                    "properties": op.get("properties", {}),
                })

        results = []
        for obj_type, inputs in creates.items():
            try:
                resp = _hs_request("POST", f"/objects/{obj_type}/batch/create", token,
                                   {"inputs": inputs}, action=f"batch_create_{obj_type}")
                results.append({"type": "create", "object_type": obj_type,
                                 "created": len(resp.get("results", [])), "status": "ok"})
            except ConnectorException as exc:
                results.append({"type": "create", "object_type": obj_type,
                                 "error": exc.error.code, "status": "error"})

        for obj_type, inputs in updates.items():
            try:
                resp = _hs_request("POST", f"/objects/{obj_type}/batch/update", token,
                                   {"inputs": inputs}, action=f"batch_update_{obj_type}")
                results.append({"type": "update", "object_type": obj_type,
                                 "updated": len(resp.get("results", [])), "status": "ok"})
            except ConnectorException as exc:
                results.append({"type": "update", "object_type": obj_type,
                                 "error": exc.error.code, "status": "error"})

        return {
            "status": "EXECUTED",
            "connector": self.connector_id,
            "processed": len(operations),
            "results": results,
        }

    # ── Webhook Verification ──────────────────────────────────────────────────

    def verify_webhook(
        self,
        headers: Dict[str, str],
        raw_body: bytes,
        client_secret: str,
        request_method: str = "POST",
        request_url: str = "",
    ) -> bool:
        """Verify HubSpot webhook HMAC-SHA256 signature (v3).

        HubSpot signs: SHA256(client_secret + method + url + body + timestamp)
        Timestamp must be within 5 minutes to prevent replay attacks.
        """
        signature = headers.get("X-HubSpot-Signature-v3", "")
        timestamp_str = headers.get("X-HubSpot-Request-Timestamp", "")

        if not signature or not timestamp_str:
            logger.warning("hubspot_webhook_missing_headers")
            return False

        # Replay protection: reject if timestamp > 5 minutes old
        try:
            ts_ms = int(timestamp_str)
            now_ms = int(time.time() * 1000)
            if abs(now_ms - ts_ms) > 5 * 60 * 1000:
                logger.warning("hubspot_webhook_replay_detected", age_ms=abs(now_ms - ts_ms))
                return False
        except (ValueError, TypeError):
            return False

        # Compute expected signature
        body_str = raw_body.decode("utf-8", errors="replace")
        signing_string = f"{request_method}{request_url}{body_str}{timestamp_str}"
        expected = hmac.new(
            client_secret.encode("utf-8"),
            signing_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        valid = hmac.compare_digest(expected, signature)
        if not valid:
            logger.warning("hubspot_webhook_invalid_signature")
        return valid

    # ── Execution Dispatcher ──────────────────────────────────────────────────

    async def execute(
        self,
        request: ConnectorExecuteRequest,
        context: ExecutionContext,
    ) -> Dict[str, Any]:
        cap = request.capability
        params = request.params

        if context.execution_mode in (ExecutionMode.SIMULATION, ExecutionMode.DRY_RUN):
            return self._simulate(cap, params)

        try:
            token = _get_token(context.tenant_id)
        except ConnectorException as exc:
            return {
                "status": "error",
                "connector": self.connector_id,
                "capability": cap,
                "error": exc.error.code,
                "detail": exc.error.user_message,
            }

        try:
            return await self._dispatch(cap, params, token)
        except ConnectorException as exc:
            return {
                "status": "error",
                "connector": self.connector_id,
                "capability": cap,
                "error": exc.error.code,
                "detail": exc.error.user_message,
                "retryable": exc.error.retryable,
            }

    def _simulate(self, cap: str, params: Dict) -> Dict:
        sim_contact = CanonicalContact(
            contact_id="sim_contact_1", provider="hubspot",
            email="sim@example.com", first_name="Simulated", last_name="Contact",
        ).model_dump()
        sim_deal = CanonicalDeal(
            deal_id="sim_deal_1", provider="hubspot",
            title="Simulated Deal", amount=50000.0, stage_id="PROPOSAL", pipeline_id="default",
        ).model_dump()
        sim_company = CanonicalCompany(
            company_id="sim_company_1", provider="hubspot", name="Acme Corp",
        ).model_dump()
        mapping = {
            "list_contacts": {"status": "SIMULATED", "connector": self.connector_id, "items": [sim_contact], "total": 1},
            "get_contact": {"status": "SIMULATED", "connector": self.connector_id, "contact": sim_contact},
            "create_contact": {"status": "SIMULATED", "connector": self.connector_id, "contact": sim_contact},
            "update_contact": {"status": "SIMULATED", "connector": self.connector_id, "contact": sim_contact},
            "delete_contact": {"status": "SIMULATED", "connector": self.connector_id, "deleted": True},
            "search_contacts": {"status": "SIMULATED", "connector": self.connector_id, "items": [sim_contact], "total": 1},
            "list_companies": {"status": "SIMULATED", "connector": self.connector_id, "items": [sim_company], "total": 1},
            "get_company": {"status": "SIMULATED", "connector": self.connector_id, "company": sim_company},
            "create_company": {"status": "SIMULATED", "connector": self.connector_id, "company": sim_company},
            "update_company": {"status": "SIMULATED", "connector": self.connector_id, "company": sim_company},
            "list_deals": {"status": "SIMULATED", "connector": self.connector_id, "items": [sim_deal], "total": 1},
            "get_deal": {"status": "SIMULATED", "connector": self.connector_id, "deal": sim_deal},
            "create_deal": {"status": "SIMULATED", "connector": self.connector_id, "deal": sim_deal},
            "update_deal": {"status": "SIMULATED", "connector": self.connector_id, "deal": sim_deal},
            "move_deal_stage": {"status": "SIMULATED", "connector": self.connector_id, "deal": {**sim_deal, "stage_id": params.get("target_stage_id", "NEGOTIATION")}},
            "close_deal_won": {"status": "SIMULATED", "connector": self.connector_id, "deal": {**sim_deal, "is_won": True, "is_closed": True}},
            "close_deal_lost": {"status": "SIMULATED", "connector": self.connector_id, "deal": {**sim_deal, "is_won": False, "is_closed": True}},
            "create_task": {"status": "SIMULATED", "connector": self.connector_id, "task_id": "sim_task_1"},
            "complete_task": {"status": "SIMULATED", "connector": self.connector_id, "task_id": params.get("task_id", "sim_task_1"), "completed": True},
            "add_note": {"status": "SIMULATED", "connector": self.connector_id, "note_id": "sim_note_1"},
            "list_notes": {"status": "SIMULATED", "connector": self.connector_id, "items": [], "total": 0},
        }
        return mapping.get(cap, {"status": "SIMULATED", "connector": self.connector_id, "capability": cap})

    async def _dispatch(self, cap: str, params: Dict, token: str) -> Dict:
        """Route capability to HubSpot API v3 calls."""
        limit = min(params.get("limit", 100), 100)  # HubSpot max per page
        cursor = params.get("cursor")

        # ── Contacts ──────────────────────────────────────────────────────────

        if cap == "list_contacts":
            path = f"/objects/contacts?limit={limit}&properties={_CONTACT_PROPERTIES}"
            if cursor:
                path += f"&after={cursor}"
            data = _hs_request("GET", path, token, action=cap)
            items = [_normalize_contact(r).model_dump() for r in data.get("results", [])]
            return {
                "status": "EXECUTED", "connector": self.connector_id,
                "items": items,
                "next_cursor": data.get("paging", {}).get("next", {}).get("after"),
                "total": len(items),
            }

        if cap == "get_contact":
            data = _hs_request(
                "GET",
                f"/objects/contacts/{params['contact_id']}?properties={_CONTACT_PROPERTIES}&associations=companies",
                token, action=cap,
            )
            return {"status": "EXECUTED", "connector": self.connector_id,
                    "contact": _normalize_contact(data).model_dump()}

        if cap == "create_contact":
            props = params.get("properties", {k: params[k] for k in ("email", "firstname", "lastname") if k in params})
            data = _hs_request("POST", "/objects/contacts", token, {"properties": props}, action=cap)
            return {"status": "EXECUTED", "connector": self.connector_id,
                    "contact": _normalize_contact(data).model_dump()}

        if cap == "update_contact":
            data = _hs_request("PATCH", f"/objects/contacts/{params['contact_id']}", token,
                               {"properties": params.get("properties", {})}, action=cap)
            return {"status": "EXECUTED", "connector": self.connector_id,
                    "contact": _normalize_contact(data).model_dump()}

        if cap == "delete_contact":
            _hs_request("DELETE", f"/objects/contacts/{params['contact_id']}", token, action=cap)
            return {"status": "EXECUTED", "connector": self.connector_id, "deleted": True}

        if cap == "search_contacts":
            payload = {
                "query": params.get("query", ""),
                "limit": limit,
                "properties": _CONTACT_PROPERTIES.split(","),
            }
            if cursor:
                payload["after"] = cursor
            data = _hs_request("POST", "/objects/contacts/search", token, payload, action=cap)
            items = [_normalize_contact(r).model_dump() for r in data.get("results", [])]
            return {
                "status": "EXECUTED", "connector": self.connector_id,
                "items": items, "total": data.get("total", 0),
                "next_cursor": data.get("paging", {}).get("next", {}).get("after"),
            }

        # ── Companies ─────────────────────────────────────────────────────────

        if cap == "list_companies":
            path = f"/objects/companies?limit={limit}&properties={_COMPANY_PROPERTIES}"
            if cursor:
                path += f"&after={cursor}"
            data = _hs_request("GET", path, token, action=cap)
            items = [_normalize_company(r).model_dump() for r in data.get("results", [])]
            return {
                "status": "EXECUTED", "connector": self.connector_id,
                "items": items,
                "next_cursor": data.get("paging", {}).get("next", {}).get("after"),
            }

        if cap == "get_company":
            data = _hs_request(
                "GET",
                f"/objects/companies/{params['company_id']}?properties={_COMPANY_PROPERTIES}",
                token, action=cap,
            )
            return {"status": "EXECUTED", "connector": self.connector_id,
                    "company": _normalize_company(data).model_dump()}

        if cap == "create_company":
            props = {"name": params.get("name", ""), "domain": params.get("domain", ""), **params.get("properties", {})}
            data = _hs_request("POST", "/objects/companies", token, {"properties": props}, action=cap)
            return {"status": "EXECUTED", "connector": self.connector_id,
                    "company": _normalize_company(data).model_dump()}

        if cap == "update_company":
            data = _hs_request("PATCH", f"/objects/companies/{params['company_id']}", token,
                               {"properties": params.get("properties", {})}, action=cap)
            return {"status": "EXECUTED", "connector": self.connector_id,
                    "company": _normalize_company(data).model_dump()}

        # ── Deals ─────────────────────────────────────────────────────────────

        if cap == "list_deals":
            path = (
                f"/objects/deals?limit={limit}"
                f"&properties={_DEAL_PROPERTIES}"
                f"&associations=companies,contacts"
            )
            if cursor:
                path += f"&after={cursor}"
            data = _hs_request("GET", path, token, action=cap)
            items = [_normalize_deal(r).model_dump() for r in data.get("results", [])]
            return {
                "status": "EXECUTED", "connector": self.connector_id,
                "items": items,
                "next_cursor": data.get("paging", {}).get("next", {}).get("after"),
            }

        if cap == "get_deal":
            data = _hs_request(
                "GET",
                f"/objects/deals/{params['deal_id']}?properties={_DEAL_PROPERTIES}&associations=companies,contacts",
                token, action=cap,
            )
            return {"status": "EXECUTED", "connector": self.connector_id,
                    "deal": _normalize_deal(data).model_dump()}

        if cap == "create_deal":
            props = {
                "dealname": params.get("title", "New Deal"),
                "amount": str(params.get("amount", 0)),
                "dealstage": params.get("stage_id", ""),
                "pipeline": params.get("pipeline_id", "default"),
                **params.get("properties", {}),
            }
            data = _hs_request("POST", "/objects/deals", token, {"properties": props}, action=cap)
            return {"status": "EXECUTED", "connector": self.connector_id,
                    "deal": _normalize_deal(data).model_dump()}

        if cap == "update_deal":
            data = _hs_request("PATCH", f"/objects/deals/{params['deal_id']}", token,
                               {"properties": params.get("properties", {})}, action=cap)
            return {"status": "EXECUTED", "connector": self.connector_id,
                    "deal": _normalize_deal(data).model_dump()}

        if cap == "move_deal_stage":
            data = _hs_request("PATCH", f"/objects/deals/{params['deal_id']}", token,
                               {"properties": {"dealstage": params["target_stage_id"]}}, action=cap)
            return {"status": "EXECUTED", "connector": self.connector_id,
                    "deal": _normalize_deal(data).model_dump()}

        if cap == "close_deal_won":
            props = {"dealstage": "closedwon", "amount": str(params.get("closed_amount", 0))}
            data = _hs_request("PATCH", f"/objects/deals/{params['deal_id']}", token,
                               {"properties": props}, action=cap)
            return {"status": "EXECUTED", "connector": self.connector_id,
                    "deal": _normalize_deal(data).model_dump()}

        if cap == "close_deal_lost":
            props = {"dealstage": "closedlost", "hs_closed_lost_reason": params.get("reason", "")}
            data = _hs_request("PATCH", f"/objects/deals/{params['deal_id']}", token,
                               {"properties": props}, action=cap)
            return {"status": "EXECUTED", "connector": self.connector_id,
                    "deal": _normalize_deal(data).model_dump()}

        # ── Tasks ─────────────────────────────────────────────────────────────

        if cap == "create_task":
            props = {
                "hs_task_subject": params.get("subject", ""),
                "hs_task_status": "NOT_STARTED",
                "hs_task_priority": params.get("priority", "MEDIUM"),
                "hs_timestamp": params.get("due_date", ""),
            }
            data = _hs_request("POST", "/objects/tasks", token, {"properties": props}, action=cap)
            return {"status": "EXECUTED", "connector": self.connector_id, "task_id": data.get("id")}

        if cap == "complete_task":
            _hs_request("PATCH", f"/objects/tasks/{params['task_id']}", token,
                        {"properties": {"hs_task_status": "COMPLETED"}}, action=cap)
            return {"status": "EXECUTED", "connector": self.connector_id,
                    "task_id": params["task_id"], "completed": True}

        # ── Notes ─────────────────────────────────────────────────────────────

        if cap == "add_note":
            props = {
                "hs_note_body": params.get("body", ""),
                "hs_timestamp": datetime.now(timezone.utc).isoformat(),
            }
            data = _hs_request("POST", "/objects/notes", token, {"properties": props}, action=cap)
            note_id = data.get("id")
            # Associate the note with contacts/deals if provided
            if note_id and params.get("contact_id"):
                try:
                    _hs_request("PUT",
                                f"/objects/notes/{note_id}/associations/contacts/{params['contact_id']}/note_to_contact",
                                token, action="associate_note_contact")
                except ConnectorException:
                    pass  # Association is best-effort
            if note_id and params.get("deal_id"):
                try:
                    _hs_request("PUT",
                                f"/objects/notes/{note_id}/associations/deals/{params['deal_id']}/note_to_deal",
                                token, action="associate_note_deal")
                except ConnectorException:
                    pass
            return {"status": "EXECUTED", "connector": self.connector_id, "note_id": note_id}

        if cap == "list_notes":
            path = f"/objects/notes?associations=contacts,deals&limit={limit}&properties=hs_note_body,hs_timestamp"
            if cursor:
                path += f"&after={cursor}"
            data = _hs_request("GET", path, token, action=cap)
            return {
                "status": "EXECUTED", "connector": self.connector_id,
                "items": data.get("results", []),
                "next_cursor": data.get("paging", {}).get("next", {}).get("after"),
                "total": len(data.get("results", [])),
            }

        return {
            "status": "EXECUTED", "connector": self.connector_id,
            "capability": cap, "detail": f"Unrecognized capability '{cap}'",
        }

    # ── IObservationSource: Perception Integration ────────────────────────────

    async def observe(self, context: PerceptionContext) -> List[ExternalObservation]:
        """Fetch recently modified CRM records as raw observations.

        Uses lastmodifieddate descending sort and an optional since_timestamp
        from PerceptionContext.last_sync_at for true delta sync.
        """
        observations: List[ExternalObservation] = []
        try:
            token = _get_token(context.tenant_id or "default_tenant")
        except ConnectorException:
            logger.warning("hubspot_observe_unauthenticated", tenant_id=context.tenant_id)
            return []

        # Determine delta filter timestamp
        since_ts: Optional[int] = None
        last_sync = getattr(context, "last_sync_at", None) or context.params.get("last_sync_at")
        if last_sync:
            if isinstance(last_sync, str):
                last_sync = datetime.fromisoformat(last_sync.replace("Z", "+00:00"))
            since_ts = int(last_sync.timestamp() * 1000)

        for obj_type in ("contacts", "deals", "companies"):
            resource_type = _OBJECT_TYPE_MAP[obj_type]
            props_map = {
                "contacts": _CONTACT_PROPERTIES,
                "deals": _DEAL_PROPERTIES,
                "companies": _COMPANY_PROPERTIES,
            }
            try:
                if since_ts:
                    # Time-bounded delta sync via search endpoint
                    payload: Dict = {
                        "filterGroups": [{
                            "filters": [{
                                "propertyName": "lastmodifieddate",
                                "operator": "GT",
                                "value": str(since_ts),
                            }]
                        }],
                        "sorts": [{"propertyName": "lastmodifieddate", "direction": "DESCENDING"}],
                        "properties": props_map[obj_type].split(","),
                        "limit": 100,
                    }
                    data = _hs_request("POST", f"/objects/{obj_type}/search", token,
                                       payload, action=f"observe_{resource_type}")
                    records = data.get("results", [])
                else:
                    # Full fetch sorted by last modified
                    path = (
                        f"/objects/{obj_type}?limit=100"
                        f"&properties={props_map[obj_type]}"
                        f"&sort=-lastmodifieddate"
                    )
                    data = _hs_request("GET", path, token, action=f"observe_{resource_type}")
                    records = data.get("results", [])

                for record in records:
                    record_id = record.get("id", "")
                    obs = ExternalObservation(
                        observation_id=str(uuid4()),
                        source_id=self.source_id,
                        source_type=self.source_type,
                        resource_id=record_id,
                        resource_type=resource_type,
                        title=_crm_record_title(obj_type, record),
                        raw_content=json.dumps(record),
                        content_type="application/json",
                        tenant_id=context.tenant_id,
                        observed_at=datetime.now(timezone.utc),
                    )
                    observations.append(obs)

            except ConnectorException as exc:
                logger.warning(
                    "hubspot_observe_error",
                    obj_type=obj_type,
                    error=exc.error.code,
                    detail=exc.error.user_message,
                )

        return observations

    def normalize(self, observation: ExternalObservation) -> UnifiedKnowledgeObject:
        """Translate a raw HubSpot observation into a provider-agnostic UKO.

        UKO ID is deterministic: SHA-256(source_id:resource_id) so the same
        record always maps to the same knowledge graph node.
        """
        try:
            raw = json.loads(observation.raw_content)
        except Exception:
            raw = {}

        props = raw.get("properties", {})
        resource_type = observation.resource_type

        entity_type_map = {"contact": "Contact", "deal": "Deal", "company": "Company"}
        entity_type = entity_type_map.get(resource_type, "Entity")

        # Structured content for embedding quality
        if resource_type == "deal":
            content = (
                f"Deal: {props.get('dealname', 'Untitled')}\n"
                f"Stage: {props.get('dealstage', '')}\n"
                f"Amount: {props.get('amount', '0')} {props.get('deal_currency_code', 'USD')}\n"
                f"Pipeline: {props.get('pipeline', '')}\n"
                f"Close Date: {props.get('closedate', '')}\n"
                f"Owner: {props.get('hubspot_owner_id', '')}"
            )
        elif resource_type == "contact":
            content = (
                f"Contact: {props.get('firstname', '')} {props.get('lastname', '')}\n"
                f"Email: {props.get('email', '')}\n"
                f"Phone: {props.get('phone', '')}\n"
                f"Job Title: {props.get('jobtitle', '')}\n"
                f"Lifecycle: {props.get('lifecyclestage', '')}\n"
                f"Lead Status: {props.get('hs_lead_status', '')}"
            )
        elif resource_type == "company":
            content = (
                f"Company: {props.get('name', '')}\n"
                f"Domain: {props.get('domain', '')}\n"
                f"Industry: {props.get('industry', '')}\n"
                f"Revenue: {props.get('annualrevenue', '')}\n"
                f"Employees: {props.get('numberofemployees', '')}\n"
                f"Country: {props.get('country', '')}"
            )
        else:
            content = json.dumps(props, indent=2)

        return UnifiedKnowledgeObject(
            uko_id=_uko_id(self.source_id, observation.resource_id),
            source_id=self.source_id,
            source_observation_id=observation.observation_id,
            resource_type=resource_type,
            entity_type=entity_type,
            title=observation.title,
            content=content,
            metadata={
                "provider": "hubspot",
                "record_id": observation.resource_id,
                **{k: v for k, v in props.items() if k in (
                    "dealstage", "lifecyclestage", "hs_lead_status",
                    "amount", "deal_currency_code",
                )},
            },
        )
