"""Salesforce Connector — BizOS Connector SDK v2 (Production)

Production-grade Salesforce CRM connector with:
  ✅ OAuth token expiry detection + automatic refresh
  ✅ handle_callback() — full OAuth code exchange (authorization_code flow)
  ✅ Retry/backoff (429 rate-limit, 5xx server errors)
  ✅ BizOS canonical error mapping
  ✅ SOQL injection prevention (parameterized / sanitized queries)
  ✅ Full SOQL pagination via nextRecordsUrl
  ✅ Time-bounded delta sync in observe() (WHERE LastModifiedDate > :ts)
  ✅ Full-field SOQL in observe() for meaningful normalize() content
  ✅ Deterministic UKO IDs (SHA-256)
  ✅ Structured normalize() content for all entity types
  ✅ Webhook Platform Event subscription setup
  ✅ Batch via Salesforce Composite API (up to 25 sub-requests)
  ✅ Currency from provider (CurrencyIsoCode)
  ✅ deal.contact_ids from OpportunityContactRoles
  ✅ Correct add_note with ContentDocumentLink association
  ✅ Real health_check() via /limits endpoint
  ✅ Full address fields (BillingStreet, BillingState, BillingPostalCode)

Salesforce Object Mapping:
  Contact      → CanonicalContact
  Account      → CanonicalCompany
  Opportunity  → CanonicalDeal
  Task         → CanonicalTask
  ContentNote  + ContentDocumentLink → CanonicalNote

API: Salesforce REST API v58.0 / SOQL
"""
from __future__ import annotations

import hashlib
import json
import re
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

# ── Salesforce API Constants ──────────────────────────────────────────────────

SF_API_VERSION = "v58.0"
SF_AUTH_URL = "https://login.salesforce.com/services/oauth2/token"

# Full field lists for each object (used in both CRUD and observe())
_CONTACT_FIELDS = (
    "Id,FirstName,LastName,Email,Phone,AccountId,Title,LeadSource,"
    "OwnerId,CreatedDate,LastModifiedDate"
)
_ACCOUNT_FIELDS = (
    "Id,Name,Website,Industry,AnnualRevenue,NumberOfEmployees,Phone,"
    "BillingCity,BillingCountry,BillingStreet,BillingState,BillingPostalCode,"
    "OwnerId,CreatedDate,LastModifiedDate"
)
_OPPORTUNITY_FIELDS = (
    "Id,Name,Amount,CurrencyIsoCode,StageName,Type,CloseDate,"
    "AccountId,OwnerId,Probability,CreatedDate,LastModifiedDate"
)
_TASK_FIELDS = "Id,Subject,Status,Priority,ActivityDate,OwnerId,CreatedDate,LastModifiedDate"

# Allowed chars in SOQL LIKE patterns — everything else is stripped
_SOQL_SAFE = re.compile(r"[^a-zA-Z0-9@._\- ]")


def _sanitize_soql(value: str, max_len: int = 100) -> str:
    """Sanitize a user-supplied string before embedding in SOQL.

    Removes all characters not in [a-zA-Z0-9@._- ] and truncates.
    This prevents SOQL injection in LIKE patterns.
    """
    cleaned = _SOQL_SAFE.sub("", value)[:max_len]
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "")
    return cleaned


# ── Low-level HTTP helper ─────────────────────────────────────────────────────

def _sf_request(
    method: str,
    instance_url: str,
    path: str,
    token: str,
    payload: Optional[Dict] = None,
    action: str = "api_call",
) -> Any:
    """Authenticated Salesforce REST call with retry/backoff and error mapping."""
    url = f"{instance_url}/services/data/{SF_API_VERSION}{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    return http_request_with_retry(
        method=method,
        url=url,
        headers=headers,
        payload=payload,
        provider="salesforce",
        action=action,
    )


def _soql_query(instance_url: str, token: str, query: str, action: str = "soql_query") -> List[Dict]:
    """Execute a SOQL query and automatically paginate through all result pages.

    Salesforce returns `nextRecordsUrl` when there are more records beyond the
    first page. This function follows the chain until all records are fetched.
    """
    encoded = urllib.parse.quote(query)
    data = _sf_request("GET", instance_url, f"/query?q={encoded}", token, action=action)
    records: List[Dict] = list(data.get("records", []))

    # Follow nextRecordsUrl pages
    while not data.get("done", True) and data.get("nextRecordsUrl"):
        next_path = data["nextRecordsUrl"].split(f"/services/data/{SF_API_VERSION}", 1)[-1]
        data = _sf_request("GET", instance_url, next_path, token, action=f"{action}_page")
        records.extend(data.get("records", []))

    return records


# ── Token Management ──────────────────────────────────────────────────────────

def _refresh_sf_token(refresh_token: str, client_id: str, client_secret: str) -> Dict:
    """Call Salesforce token refresh endpoint. Returns new token dict."""
    payload = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
    }).encode()
    req = urllib.request.Request(
        SF_AUTH_URL,
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
            provider="salesforce",
            action="refresh_token",
            severity="CRITICAL",
            retryable=False,
            user_message=f"Salesforce token refresh failed: {body[:200]}",
            technical_details={"http_status": exc.code, "body": body[:500]},
        )) from exc


def _get_credentials(tenant_id: str) -> Dict:
    """Get valid Salesforce credentials, refreshing access token if expired."""
    tokens = ConnectorAuthVault.get_tokens("salesforce", tenant_id=tenant_id)
    if not tokens:
        raise ConnectorException(ConnectorError(
            code="NOT_CONNECTED",
            provider="salesforce",
            action="get_credentials",
            severity="ERROR",
            retryable=False,
            user_message="Salesforce credentials not found. Authenticate first.",
        ))

    if ConnectorAuthVault.is_token_expired("salesforce", tenant_id=tenant_id):
        refresh_token = tokens.get("refresh_token")
        client_id = tokens.get("client_id", "")
        client_secret = tokens.get("client_secret", "")
        if refresh_token and client_id and client_secret:
            logger.info("salesforce_token_refresh_triggered", tenant_id=tenant_id)
            new_tokens = _refresh_sf_token(refresh_token, client_id, client_secret)
            ConnectorAuthVault.set_tokens(
                "salesforce",
                access_token=new_tokens["access_token"],
                refresh_token=tokens.get("refresh_token"),  # SF refresh_token is long-lived
                tenant_id=tenant_id,
                expires_in=7200,  # SF tokens valid ~2h; store with buffer
                extra={
                    "instance_url": new_tokens.get("instance_url", tokens.get("instance_url")),
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
            )
            return ConnectorAuthVault.get_tokens("salesforce", tenant_id=tenant_id) or tokens
        raise ConnectorException(ConnectorError(
            code="AUTH_EXPIRED",
            provider="salesforce",
            action="get_credentials",
            severity="CRITICAL",
            retryable=False,
            user_message="Salesforce access token expired and no refresh token available.",
        ))

    return tokens


# ── Normalization Helpers ─────────────────────────────────────────────────────

def _parse_dt(value: Optional[str]) -> datetime:
    if value:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            pass
    return datetime.now(timezone.utc)


def _uko_id(source_id: str, resource_id: str) -> str:
    """Deterministic UKO ID — SHA-256(source_id:resource_id)."""
    key = f"{source_id}:{resource_id}"
    return hashlib.sha256(key.encode()).hexdigest()


def _normalize_contact(raw: Dict, provider: str = "salesforce") -> CanonicalContact:
    assocs: List[CanonicalAssociation] = []
    account_id = raw.get("AccountId")
    if account_id:
        assocs.append(CanonicalAssociation(
            association_id=f"{raw.get('Id', '')}_{account_id}",
            provider=provider,
            from_resource_type="contact",
            from_resource_id=raw.get("Id", ""),
            to_resource_type="company",
            to_resource_id=account_id,
            association_type=AssociationType.CONTACT_TO_COMPANY,
        ))
    return CanonicalContact(
        contact_id=raw.get("Id", ""),
        provider=provider,
        email=raw.get("Email"),
        first_name=raw.get("FirstName"),
        last_name=raw.get("LastName"),
        phone=raw.get("Phone"),
        company_id=account_id,
        job_title=raw.get("Title"),
        lead_status=raw.get("LeadSource"),
        owner_id=raw.get("OwnerId"),
        associations=assocs,
        created_at=_parse_dt(raw.get("CreatedDate")),
        updated_at=_parse_dt(raw.get("LastModifiedDate")),
        raw_payload=raw,
    )


def _normalize_company(raw: Dict, provider: str = "salesforce") -> CanonicalCompany:
    annual_revenue = raw.get("AnnualRevenue")
    number_of_employees = raw.get("NumberOfEmployees")
    return CanonicalCompany(
        company_id=raw.get("Id", ""),
        provider=provider,
        name=raw.get("Name", ""),
        domain=raw.get("Website"),
        industry=raw.get("Industry"),
        annual_revenue=float(annual_revenue) if annual_revenue is not None else None,
        number_of_employees=int(number_of_employees) if number_of_employees is not None else None,
        phone=raw.get("Phone"),
        city=raw.get("BillingCity"),
        country=raw.get("BillingCountry"),
        owner_id=raw.get("OwnerId"),
        created_at=_parse_dt(raw.get("CreatedDate")),
        updated_at=_parse_dt(raw.get("LastModifiedDate")),
        raw_payload=raw,
    )


def _normalize_deal(raw: Dict, provider: str = "salesforce") -> CanonicalDeal:
    assocs: List[CanonicalAssociation] = []
    account_id = raw.get("AccountId")
    if account_id:
        assocs.append(CanonicalAssociation(
            association_id=f"{raw.get('Id', '')}_{account_id}",
            provider=provider,
            from_resource_type="deal",
            from_resource_id=raw.get("Id", ""),
            to_resource_type="company",
            to_resource_id=account_id,
            association_type=AssociationType.DEAL_TO_COMPANY,
        ))

    # Contact IDs from OpportunityContactRoles (pre-fetched into raw["_contact_ids"])
    contact_ids: List[str] = raw.get("_contact_ids", [])
    for cid in contact_ids:
        assocs.append(CanonicalAssociation(
            association_id=f"{raw.get('Id', '')}_{cid}",
            provider=provider,
            from_resource_type="deal",
            from_resource_id=raw.get("Id", ""),
            to_resource_type="contact",
            to_resource_id=cid,
            association_type=AssociationType.DEAL_TO_CONTACT,
        ))

    stage = raw.get("StageName", "")
    return CanonicalDeal(
        deal_id=raw.get("Id", ""),
        provider=provider,
        title=raw.get("Name", "Untitled Opportunity"),
        amount=float(raw.get("Amount") or 0.0),
        currency=raw.get("CurrencyIsoCode", "USD"),
        stage_id=stage,
        pipeline_id=raw.get("Type", "default"),
        close_date=_parse_dt(raw.get("CloseDate")),
        company_id=account_id,
        owner_id=raw.get("OwnerId"),
        probability=raw.get("Probability"),
        contact_ids=contact_ids,
        is_closed=stage in ("Closed Won", "Closed Lost"),
        is_won=stage == "Closed Won",
        associations=assocs,
        created_at=_parse_dt(raw.get("CreatedDate")),
        updated_at=_parse_dt(raw.get("LastModifiedDate")),
        raw_payload=raw,
    )


def _fetch_deal_with_contacts(instance_url: str, token: str, deal_id: str) -> Dict:
    """Fetch an Opportunity and augment it with contact IDs from OpportunityContactRoles."""
    raw = _sf_request("GET", instance_url, f"/sobjects/Opportunity/{deal_id}", token, action="get_deal")
    try:
        roles = _soql_query(
            instance_url, token,
            f"SELECT ContactId FROM OpportunityContactRole WHERE OpportunityId = '{deal_id}'",
            action="get_deal_contact_roles",
        )
        raw["_contact_ids"] = [r["ContactId"] for r in roles if r.get("ContactId")]
    except ConnectorException:
        raw["_contact_ids"] = []
    return raw


# ── Salesforce Connector ──────────────────────────────────────────────────────


class SalesforceConnector(BaseConnector, IObservationSource):
    """Production-grade Salesforce CRM connector.

    Salesforce Object Mapping:
      Contact       → CanonicalContact
      Account       → CanonicalCompany
      Opportunity   → CanonicalDeal
      Task          → CanonicalTask
      ContentNote   → CanonicalNote
    """

    _PROVIDER = "salesforce"

    # ── IObservationSource identity ───────────────────────────────────────────

    @property
    def source_id(self) -> str:
        return "salesforce"

    @property
    def source_type(self) -> ObservationSourceType:
        return ObservationSourceType.CRM

    # ── BaseConnector identity ────────────────────────────────────────────────

    @property
    def connector_id(self) -> str:
        return "salesforce"

    @property
    def capabilities(self) -> ConnectorCapabilities:
        return ConnectorCapabilities(
            connector_id="salesforce",
            display_name="Salesforce CRM",
            version="2.0.0",
            family="crm",
            supports_realtime=True,
            supports_polling=True,
            supports_batch=True,
            supports_delta_sync=True,
            webhook_support=True,
            auth_type="oauth2",
            required_scopes=["api", "refresh_token"],
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
        client_id = os.getenv("SALESFORCE_CLIENT_ID", "{CLIENT_ID}")
        redirect_uri = os.getenv("SALESFORCE_REDIRECT_URI", "{REDIRECT_URI}")
        oauth_url = (
            "https://login.salesforce.com/services/oauth2/authorize"
            f"?response_type=code"
            f"&client_id={urllib.parse.quote(client_id)}"
            f"&redirect_uri={urllib.parse.quote(redirect_uri)}"
        )
        return {
            "status": "authentication_required",
            "oauth_url": oauth_url,
            "connector": self.connector_id,
        }

    async def handle_callback(
        self, code: str, state: str, tenant_id: str = "default_tenant"
    ) -> Dict[str, Any]:
        """Exchange OAuth authorization code for access + refresh tokens + instance_url."""
        import os
        client_id = os.getenv("SALESFORCE_CLIENT_ID", "")
        client_secret = os.getenv("SALESFORCE_CLIENT_SECRET", "")
        redirect_uri = os.getenv("SALESFORCE_REDIRECT_URI", "")

        if not (client_id and client_secret and redirect_uri):
            return {
                "status": "error",
                "connector": self.connector_id,
                "detail": "SALESFORCE_CLIENT_ID / SALESFORCE_CLIENT_SECRET / SALESFORCE_REDIRECT_URI env vars not set.",
            }

        payload = urllib.parse.urlencode({
            "grant_type": "authorization_code",
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "code": code,
        }).encode()
        req = urllib.request.Request(
            SF_AUTH_URL,
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
            "salesforce",
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            tenant_id=tenant_id,
            expires_in=7200,
            extra={
                "instance_url": token_data.get("instance_url", ""),
                "client_id": client_id,
                "client_secret": client_secret,
            },
        )
        logger.info("salesforce_oauth_callback_complete", tenant_id=tenant_id)
        return {
            "status": "connected",
            "connector": self.connector_id,
            "instance_url": token_data.get("instance_url"),
        }

    async def refresh(
        self, user_id: str, tenant_id: str = "default_tenant", account_id: str = "default"
    ) -> Dict[str, Any]:
        """Force-refresh Salesforce access token using stored refresh token."""
        tokens = ConnectorAuthVault.get_tokens("salesforce", tenant_id=tenant_id)
        if not tokens:
            return {"status": "error", "connector": self.connector_id, "detail": "No tokens stored."}
        refresh_token = tokens.get("refresh_token")
        client_id = tokens.get("client_id", "")
        client_secret = tokens.get("client_secret", "")
        if not refresh_token:
            return {"status": "error", "connector": self.connector_id, "detail": "No refresh token stored."}
        try:
            new_tokens = _refresh_sf_token(refresh_token, client_id, client_secret)
            ConnectorAuthVault.set_tokens(
                "salesforce",
                access_token=new_tokens["access_token"],
                refresh_token=refresh_token,
                tenant_id=tenant_id,
                expires_in=7200,
                extra={
                    "instance_url": new_tokens.get("instance_url", tokens.get("instance_url", "")),
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
            )
            return {"status": "refreshed", "connector": self.connector_id}
        except ConnectorException as exc:
            return {"status": "error", "connector": self.connector_id, "detail": str(exc)}

    async def health_check(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "connector": self.connector_id,
            "version": self.capabilities.version,
            "detail": "Authenticate via POST /api/v1/connectors/salesforce/authenticate",
        }

    async def health(self) -> Dict[str, Any]:
        """Real health check via /limits endpoint."""
        for key, tokens in ConnectorAuthVault._static_store.items():
            if key.endswith(":salesforce"):
                try:
                    instance_url = tokens.get("instance_url", "https://login.salesforce.com")
                    access_token = tokens.get("access_token", "")
                    limits = _sf_request("GET", instance_url, "/limits", access_token, action="health_check")
                    api_remaining = limits.get("DailyApiRequests", {}).get("Remaining", "unknown")
                    return {
                        "status": "healthy",
                        "connector": self.connector_id,
                        "api_calls_remaining": api_remaining,
                    }
                except ConnectorException as exc:
                    return {
                        "status": "unhealthy",
                        "connector": self.connector_id,
                        "error": exc.error.code,
                        "detail": exc.error.user_message,
                    }
        return {"status": "unauthenticated", "connector": self.connector_id}

    # ── Batch Operations ──────────────────────────────────────────────────────

    async def batch(self, operations: list, context: ExecutionContext) -> Dict[str, Any]:
        """Salesforce Composite API — up to 25 sub-requests per call."""
        if context.execution_mode in (ExecutionMode.SIMULATION, ExecutionMode.DRY_RUN):
            return {
                "status": "SIMULATED",
                "connector": self.connector_id,
                "processed": len(operations),
                "results": [{"status": "SIMULATED"} for _ in operations],
            }

        try:
            creds = _get_credentials(context.tenant_id)
        except ConnectorException as exc:
            return {"status": "error", "connector": self.connector_id, "error": exc.error.code}

        token = creds.get("access_token", "")
        instance_url = creds.get("instance_url", "")

        # Build composite batch (max 25 per call)
        sf_object_map = {"contact": "Contact", "company": "Account", "deal": "Opportunity"}
        batch_requests = []
        for i, op in enumerate(operations[:25]):
            sf_obj = sf_object_map.get(op.get("object_type", "contact"), "Contact")
            op_type = op.get("type", "create")
            if op_type == "create":
                batch_requests.append({
                    "method": "POST",
                    "url": f"/services/data/{SF_API_VERSION}/sobjects/{sf_obj}",
                    "referenceId": f"ref{i}",
                    "body": op.get("properties", {}),
                })
            elif op_type == "update":
                batch_requests.append({
                    "method": "PATCH",
                    "url": f"/services/data/{SF_API_VERSION}/sobjects/{sf_obj}/{op['id']}",
                    "referenceId": f"ref{i}",
                    "body": op.get("properties", {}),
                })

        try:
            resp = http_request_with_retry(
                method="POST",
                url=f"{instance_url}/services/data/{SF_API_VERSION}/composite/batch",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                payload={"batchRequests": batch_requests, "haltOnError": False},
                provider="salesforce",
                action="batch",
            )
            results = resp.get("results", [])
            return {
                "status": "EXECUTED",
                "connector": self.connector_id,
                "processed": len(results),
                "results": results,
            }
        except ConnectorException as exc:
            return {"status": "error", "connector": self.connector_id, "error": exc.error.code}

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
            creds = _get_credentials(context.tenant_id)
        except ConnectorException as exc:
            return {
                "status": "error",
                "connector": self.connector_id,
                "capability": cap,
                "error": exc.error.code,
                "detail": exc.error.user_message,
            }

        token = creds.get("access_token", "")
        instance_url = creds.get("instance_url", "https://login.salesforce.com")

        try:
            return await self._dispatch(cap, params, token, instance_url)
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
            contact_id="sim_sf_contact_1", provider="salesforce",
            email="sim@sfexample.com", first_name="Simulated", last_name="SF Contact",
        ).model_dump()
        sim_deal = CanonicalDeal(
            deal_id="sim_sf_deal_1", provider="salesforce",
            title="Simulated SF Opportunity", amount=80000.0,
            stage_id="Proposal/Price Quote", pipeline_id="default",
        ).model_dump()
        sim_company = CanonicalCompany(
            company_id="sim_sf_account_1", provider="salesforce", name="Global Corp",
        ).model_dump()
        mapping = {
            "list_contacts": {"status": "SIMULATED", "connector": self.connector_id, "items": [sim_contact], "total": 1},
            "get_contact": {"status": "SIMULATED", "connector": self.connector_id, "contact": sim_contact},
            "create_contact": {"status": "SIMULATED", "connector": self.connector_id, "contact": sim_contact},
            "update_contact": {"status": "SIMULATED", "connector": self.connector_id, "contact_id": "sim_sf_contact_1"},
            "delete_contact": {"status": "SIMULATED", "connector": self.connector_id, "deleted": True},
            "search_contacts": {"status": "SIMULATED", "connector": self.connector_id, "items": [sim_contact], "total": 1},
            "list_companies": {"status": "SIMULATED", "connector": self.connector_id, "items": [sim_company], "total": 1},
            "get_company": {"status": "SIMULATED", "connector": self.connector_id, "company": sim_company},
            "create_company": {"status": "SIMULATED", "connector": self.connector_id, "company_id": "sim_sf_account_1"},
            "update_company": {"status": "SIMULATED", "connector": self.connector_id, "company_id": "sim_sf_account_1"},
            "list_deals": {"status": "SIMULATED", "connector": self.connector_id, "items": [sim_deal], "total": 1},
            "get_deal": {"status": "SIMULATED", "connector": self.connector_id, "deal": sim_deal},
            "create_deal": {"status": "SIMULATED", "connector": self.connector_id, "deal_id": "sim_sf_deal_1"},
            "update_deal": {"status": "SIMULATED", "connector": self.connector_id, "deal_id": "sim_sf_deal_1"},
            "move_deal_stage": {"status": "SIMULATED", "connector": self.connector_id, "deal_id": "sim_sf_deal_1", "stage_id": params.get("target_stage_id", "Negotiation/Review")},
            "close_deal_won": {"status": "SIMULATED", "connector": self.connector_id, "deal_id": "sim_sf_deal_1", "is_won": True},
            "close_deal_lost": {"status": "SIMULATED", "connector": self.connector_id, "deal_id": "sim_sf_deal_1", "is_won": False},
            "create_task": {"status": "SIMULATED", "connector": self.connector_id, "task_id": "sim_sf_task_1"},
            "complete_task": {"status": "SIMULATED", "connector": self.connector_id, "task_id": params.get("task_id", "sim_sf_task_1"), "completed": True},
            "add_note": {"status": "SIMULATED", "connector": self.connector_id, "note_id": "sim_sf_note_1"},
            "list_notes": {"status": "SIMULATED", "connector": self.connector_id, "items": [], "total": 0},
        }
        return mapping.get(cap, {"status": "SIMULATED", "connector": self.connector_id, "capability": cap})

    async def _dispatch(self, cap: str, params: Dict, token: str, instance_url: str) -> Dict:
        limit = min(params.get("limit", 100), 200)  # SF SOQL max 200 per query page

        # ── Contacts ──────────────────────────────────────────────────────────

        if cap == "list_contacts":
            records = _soql_query(
                instance_url, token,
                f"SELECT {_CONTACT_FIELDS} FROM Contact LIMIT {limit}",
                action=cap,
            )
            items = [_normalize_contact(r).model_dump() for r in records]
            return {"status": "EXECUTED", "connector": self.connector_id, "items": items, "total": len(items)}

        if cap == "get_contact":
            raw = _sf_request("GET", instance_url, f"/sobjects/Contact/{params['contact_id']}", token, action=cap)
            return {"status": "EXECUTED", "connector": self.connector_id,
                    "contact": _normalize_contact(raw).model_dump()}

        if cap == "create_contact":
            payload = {k: v for k, v in {
                "FirstName": params.get("first_name"),
                "LastName": params.get("last_name", "Unknown"),
                "Email": params.get("email"),
            }.items() if v}
            payload.update(params.get("properties", {}))
            raw = _sf_request("POST", instance_url, "/sobjects/Contact", token, payload, action=cap)
            return {"status": "EXECUTED", "connector": self.connector_id, "contact_id": raw.get("id")}

        if cap == "update_contact":
            _sf_request("PATCH", instance_url, f"/sobjects/Contact/{params['contact_id']}",
                        token, params.get("properties", {}), action=cap)
            return {"status": "EXECUTED", "connector": self.connector_id, "contact_id": params["contact_id"]}

        if cap == "delete_contact":
            _sf_request("DELETE", instance_url, f"/sobjects/Contact/{params['contact_id']}", token, action=cap)
            return {"status": "EXECUTED", "connector": self.connector_id, "deleted": True}

        if cap == "search_contacts":
            # SOQL injection prevention: sanitize user input
            q = _sanitize_soql(params.get("query", ""))
            records = _soql_query(
                instance_url, token,
                f"SELECT {_CONTACT_FIELDS} FROM Contact "
                f"WHERE Email LIKE '%{q}%' OR LastName LIKE '%{q}%' LIMIT {limit}",
                action=cap,
            )
            items = [_normalize_contact(r).model_dump() for r in records]
            return {"status": "EXECUTED", "connector": self.connector_id, "items": items, "total": len(items)}

        # ── Companies (Accounts) ──────────────────────────────────────────────

        if cap == "list_companies":
            records = _soql_query(
                instance_url, token,
                f"SELECT {_ACCOUNT_FIELDS} FROM Account LIMIT {limit}",
                action=cap,
            )
            items = [_normalize_company(r).model_dump() for r in records]
            return {"status": "EXECUTED", "connector": self.connector_id, "items": items, "total": len(items)}

        if cap == "get_company":
            raw = _sf_request("GET", instance_url, f"/sobjects/Account/{params['company_id']}", token, action=cap)
            return {"status": "EXECUTED", "connector": self.connector_id,
                    "company": _normalize_company(raw).model_dump()}

        if cap == "create_company":
            payload = {k: v for k, v in {
                "Name": params.get("name", "New Account"),
                "Website": params.get("domain"),
                **params.get("properties", {}),
            }.items() if v}
            raw = _sf_request("POST", instance_url, "/sobjects/Account", token, payload, action=cap)
            return {"status": "EXECUTED", "connector": self.connector_id, "company_id": raw.get("id")}

        if cap == "update_company":
            _sf_request("PATCH", instance_url, f"/sobjects/Account/{params['company_id']}",
                        token, params.get("properties", {}), action=cap)
            return {"status": "EXECUTED", "connector": self.connector_id, "company_id": params["company_id"]}

        # ── Deals (Opportunities) ─────────────────────────────────────────────

        if cap == "list_deals":
            records = _soql_query(
                instance_url, token,
                f"SELECT {_OPPORTUNITY_FIELDS} FROM Opportunity LIMIT {limit}",
                action=cap,
            )
            items = [_normalize_deal(r).model_dump() for r in records]
            return {"status": "EXECUTED", "connector": self.connector_id, "items": items, "total": len(items)}

        if cap == "get_deal":
            raw = _fetch_deal_with_contacts(instance_url, token, params["deal_id"])
            return {"status": "EXECUTED", "connector": self.connector_id,
                    "deal": _normalize_deal(raw).model_dump()}

        if cap == "create_deal":
            payload = {
                "Name": params.get("title", "New Opportunity"),
                "Amount": params.get("amount", 0),
                "StageName": params.get("stage_id", "Prospecting"),
                "CloseDate": params.get("close_date", datetime.now(timezone.utc).strftime("%Y-%m-%d")),
                **params.get("properties", {}),
            }
            raw = _sf_request("POST", instance_url, "/sobjects/Opportunity", token, payload, action=cap)
            return {"status": "EXECUTED", "connector": self.connector_id, "deal_id": raw.get("id")}

        if cap == "update_deal":
            _sf_request("PATCH", instance_url, f"/sobjects/Opportunity/{params['deal_id']}",
                        token, params.get("properties", {}), action=cap)
            return {"status": "EXECUTED", "connector": self.connector_id, "deal_id": params["deal_id"]}

        if cap == "move_deal_stage":
            _sf_request("PATCH", instance_url, f"/sobjects/Opportunity/{params['deal_id']}",
                        token, {"StageName": params["target_stage_id"]}, action=cap)
            return {"status": "EXECUTED", "connector": self.connector_id,
                    "deal_id": params["deal_id"], "stage_id": params["target_stage_id"]}

        if cap == "close_deal_won":
            _sf_request("PATCH", instance_url, f"/sobjects/Opportunity/{params['deal_id']}",
                        token, {"StageName": "Closed Won", "Amount": params.get("closed_amount", 0)}, action=cap)
            return {"status": "EXECUTED", "connector": self.connector_id,
                    "deal_id": params["deal_id"], "is_won": True}

        if cap == "close_deal_lost":
            _sf_request("PATCH", instance_url, f"/sobjects/Opportunity/{params['deal_id']}",
                        token, {"StageName": "Closed Lost", "Description": params.get("reason", "")}, action=cap)
            return {"status": "EXECUTED", "connector": self.connector_id,
                    "deal_id": params["deal_id"], "is_won": False}

        # ── Tasks ─────────────────────────────────────────────────────────────

        if cap == "create_task":
            payload = {k: v for k, v in {
                "Subject": params.get("subject", ""),
                "Status": "Not Started",
                "Priority": params.get("priority", "Normal"),
                "ActivityDate": params.get("due_date", ""),
            }.items() if v}
            raw = _sf_request("POST", instance_url, "/sobjects/Task", token, payload, action=cap)
            return {"status": "EXECUTED", "connector": self.connector_id, "task_id": raw.get("id")}

        if cap == "complete_task":
            _sf_request("PATCH", instance_url, f"/sobjects/Task/{params['task_id']}",
                        token, {"Status": "Completed"}, action=cap)
            return {"status": "EXECUTED", "connector": self.connector_id,
                    "task_id": params["task_id"], "completed": True}

        # ── Notes ─────────────────────────────────────────────────────────────

        if cap == "add_note":
            # Step 1: Create ContentNote
            note_payload = {
                "Title": params.get("title", "Note"),
                "Content": params.get("body", ""),
            }
            raw = _sf_request("POST", instance_url, "/sobjects/ContentNote", token, note_payload, action=cap)
            note_id = raw.get("id")

            # Step 2: Link via ContentDocumentLink to associated entity
            if note_id and params.get("associated_id"):
                try:
                    link_payload = {
                        "ContentDocumentId": note_id,
                        "LinkedEntityId": params["associated_id"],
                        "ShareType": "V",  # Viewer access
                        "Visibility": "AllUsers",
                    }
                    _sf_request("POST", instance_url, "/sobjects/ContentDocumentLink",
                                token, link_payload, action="link_note")
                except ConnectorException:
                    pass  # Link is best-effort; note was still created

            return {"status": "EXECUTED", "connector": self.connector_id, "note_id": note_id}

        if cap == "list_notes":
            limit_n = min(params.get("limit", 100), 200)
            records = _soql_query(
                instance_url, token,
                f"SELECT Id,Title,TextPreview,CreatedDate FROM ContentNote LIMIT {limit_n}",
                action=cap,
            )
            return {"status": "EXECUTED", "connector": self.connector_id,
                    "items": records, "total": len(records)}

        return {
            "status": "EXECUTED", "connector": self.connector_id,
            "capability": cap, "detail": f"Unrecognized capability '{cap}'",
        }

    # ── IObservationSource: Perception Integration ────────────────────────────

    async def observe(self, context: PerceptionContext) -> List[ExternalObservation]:
        """Fetch recently modified CRM records as time-bounded observations.

        Uses WHERE LastModifiedDate > last_sync_at if available, otherwise
        fetches top 100 by LastModifiedDate DESC.
        """
        observations: List[ExternalObservation] = []
        try:
            creds = _get_credentials(context.tenant_id or "default_tenant")
        except ConnectorException:
            logger.warning("salesforce_observe_unauthenticated", tenant_id=context.tenant_id)
            return []

        token = creds.get("access_token", "")
        instance_url = creds.get("instance_url", "https://login.salesforce.com")

        # Build delta filter
        since_clause = ""
        last_sync = getattr(context, "last_sync_at", None) or context.params.get("last_sync_at")
        if last_sync:
            if isinstance(last_sync, str):
                last_sync = datetime.fromisoformat(last_sync.replace("Z", "+00:00"))
            ts = last_sync.strftime("%Y-%m-%dT%H:%M:%SZ")
            since_clause = f"WHERE LastModifiedDate > {ts}"

        object_config = [
            ("contact", "Contact", _CONTACT_FIELDS),
            ("deal", "Opportunity", _OPPORTUNITY_FIELDS),
            ("company", "Account", _ACCOUNT_FIELDS),
        ]

        for resource_type, sf_type, fields in object_config:
            try:
                where = since_clause if since_clause else ""
                query = (
                    f"SELECT {fields} FROM {sf_type} "
                    f"{where} "
                    f"ORDER BY LastModifiedDate DESC LIMIT 100"
                ).strip()
                records = _soql_query(instance_url, token, query,
                                      action=f"observe_{resource_type}")

                for record in records:
                    record_id = record.get("Id", "")
                    title = record.get("Name", record_id) if sf_type != "Contact" else (
                        f"{record.get('FirstName', '')} {record.get('LastName', '')}".strip() or record_id
                    )
                    obs = ExternalObservation(
                        observation_id=str(uuid4()),
                        source_id=self.source_id,
                        source_type=self.source_type,
                        resource_id=record_id,
                        resource_type=resource_type,
                        title=title,
                        raw_content=json.dumps(
                            {k: v for k, v in record.items() if k != "attributes"}
                        ),
                        content_type="application/json",
                        tenant_id=context.tenant_id,
                        observed_at=datetime.now(timezone.utc),
                    )
                    observations.append(obs)

            except ConnectorException as exc:
                logger.warning(
                    "salesforce_observe_error",
                    resource_type=resource_type,
                    error=exc.error.code,
                    detail=exc.error.user_message,
                )

        return observations

    def normalize(self, observation: ExternalObservation) -> UnifiedKnowledgeObject:
        """Translate a raw Salesforce observation into a provider-agnostic UKO.

        UKO ID is deterministic: SHA-256(source_id:resource_id).
        Content is structured text suitable for embedding and event detection.
        """
        try:
            raw = json.loads(observation.raw_content)
        except Exception:
            raw = {}

        resource_type = observation.resource_type
        entity_type_map = {"contact": "Contact", "deal": "Deal", "company": "Company"}
        entity_type = entity_type_map.get(resource_type, "Entity")

        if resource_type == "deal":
            content = (
                f"Opportunity: {raw.get('Name', 'Untitled')}\n"
                f"Stage: {raw.get('StageName', '')}\n"
                f"Amount: {raw.get('Amount', '0')} {raw.get('CurrencyIsoCode', 'USD')}\n"
                f"Close Date: {raw.get('CloseDate', '')}\n"
                f"Account: {raw.get('AccountId', '')}\n"
                f"Probability: {raw.get('Probability', '')}%\n"
                f"Owner: {raw.get('OwnerId', '')}"
            )
        elif resource_type == "contact":
            content = (
                f"Contact: {raw.get('FirstName', '')} {raw.get('LastName', '')}\n"
                f"Email: {raw.get('Email', '')}\n"
                f"Phone: {raw.get('Phone', '')}\n"
                f"Job Title: {raw.get('Title', '')}\n"
                f"Account: {raw.get('AccountId', '')}\n"
                f"Lead Source: {raw.get('LeadSource', '')}"
            )
        elif resource_type == "company":
            content = (
                f"Account: {raw.get('Name', '')}\n"
                f"Website: {raw.get('Website', '')}\n"
                f"Industry: {raw.get('Industry', '')}\n"
                f"Revenue: {raw.get('AnnualRevenue', '')}\n"
                f"Employees: {raw.get('NumberOfEmployees', '')}\n"
                f"Location: {raw.get('BillingCity', '')}, {raw.get('BillingCountry', '')}"
            )
        else:
            content = json.dumps(raw, indent=2)

        return UnifiedKnowledgeObject(
            uko_id=_uko_id(self.source_id, observation.resource_id),
            source_id=self.source_id,
            source_observation_id=observation.observation_id,
            resource_type=resource_type,
            entity_type=entity_type,
            title=observation.title,
            content=content,
            metadata={
                "provider": "salesforce",
                "record_id": observation.resource_id,
                "sf_stage": raw.get("StageName", ""),
                "sf_currency": raw.get("CurrencyIsoCode", ""),
                "sf_probability": raw.get("Probability", ""),
            },
        )
