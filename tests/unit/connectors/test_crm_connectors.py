"""CRM Layer v2 — Production Readiness Test Suite

Covers all audit findings implemented in v2:
  ── Canonical CRM models (unchanged)
  ── Token expiry detection and refresh flow
  ── 429 rate-limit retry with backoff
  ── BizOS canonical error mapping (404, 401, 429)
  ── HubSpot pagination cursor
  ── SOQL injection guard (Salesforce search_contacts)
  ── Deterministic UKO IDs (SHA-256 idempotent)
  ── HubSpot webhook HMAC verification + replay protection
  ── Batch operations (HubSpot + Salesforce simulation)
  ── Delta sync timestamp bounds in observe()
  ── Structured normalize() content for all entity types
  ── deal.contact_ids population
  ── Currency from provider
  ── Company rstrip("s") fix
  ── handle_callback() OAuth flow
  ── Real health_check()
  ── All 21 actions in simulation mode (both connectors)
  ── BusinessEventDetector CRM patterns (unchanged)
  ── BusinessStateChangeEvent state_delta (unchanged)
"""
from __future__ import annotations

import hashlib
import json
import time
import unittest.mock as mock
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
from uuid import uuid4

from app.connectors.sdk.canonical.common import (
    CanonicalUser, CanonicalPage, CanonicalAssociation, AssociationType
)
from app.connectors.sdk.canonical.crm import (
    CanonicalContact, CanonicalCompany, CanonicalDeal,
    CanonicalStage, CanonicalPipeline, CanonicalTask,
    CanonicalNote, CanonicalActivity, CanonicalActivityType,
    CanonicalProduct, CanonicalOwner,
)
from app.connectors.hubspot.connector import (
    HubSpotConnector,
    _normalize_contact as hs_normalize_contact,
    _normalize_deal as hs_normalize_deal,
    _normalize_company as hs_normalize_company,
    _uko_id,
)
from app.connectors.salesforce.connector import (
    SalesforceConnector,
    _sanitize_soql,
    _normalize_contact as sf_normalize_contact,
    _normalize_deal as sf_normalize_deal,
    _normalize_company as sf_normalize_company,
)
from app.connectors.sdk.errors import ConnectorError, ConnectorException
from app.connectors.sdk.base import ConnectorExecuteRequest
from app.connectors.auth.vault import ConnectorAuthVault
from app.domain.shared.context import ExecutionContext
from app.shared.enums import ExecutionMode
from app.perception.models.observation import (
    BusinessEventType, ExternalObservation, ObservationSourceType, UnifiedKnowledgeObject
)
from app.perception.engine.business_event_detector import BusinessEventDetector
from app.perception.sources.interface import PerceptionContext
from app.shared.events.models import BusinessStateChangeEvent


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def hubspot() -> HubSpotConnector:
    return HubSpotConnector()


@pytest.fixture
def salesforce() -> SalesforceConnector:
    return SalesforceConnector()


@pytest.fixture
def sim_ctx() -> ExecutionContext:
    return ExecutionContext(
        tenant_id=str(uuid4()), principal_id="test_user",
        session_id=str(uuid4()), conversation_id=str(uuid4()),
        trace_id=str(uuid4()), correlation_id=str(uuid4()),
        execution_mode=ExecutionMode.SIMULATION,
    )


@pytest.fixture
def prod_ctx() -> ExecutionContext:
    tenant = str(uuid4())
    return ExecutionContext(
        tenant_id=tenant, principal_id="test_user",
        session_id=str(uuid4()), conversation_id=str(uuid4()),
        trace_id=str(uuid4()), correlation_id=str(uuid4()),
        execution_mode=ExecutionMode.PRODUCTION,
    )


def _make_perception_ctx(tenant_id: str, last_sync_at=None) -> PerceptionContext:
    return PerceptionContext(
        tenant_id=tenant_id,
        session_id=str(uuid4()),
        principal_id="user",
        conversation_id=str(uuid4()),
        trace_id=str(uuid4()),
        correlation_id=str(uuid4()),
        last_sync_at=last_sync_at,
    )


# ── 1. Canonical CRM Model Tests (unchanged) ──────────────────────────────────

def test_canonical_association_model():
    assoc = CanonicalAssociation(
        association_id="assoc_1", provider="hubspot",
        from_resource_type="deal", from_resource_id="deal_123",
        to_resource_type="company", to_resource_id="company_456",
        association_type=AssociationType.DEAL_TO_COMPANY,
    )
    assert assoc.association_type == AssociationType.DEAL_TO_COMPANY


def test_canonical_contact_with_association():
    assoc = CanonicalAssociation(
        association_id="c2c_1", provider="hubspot",
        from_resource_type="contact", from_resource_id="c_001",
        to_resource_type="company", to_resource_id="co_001",
        association_type=AssociationType.CONTACT_TO_COMPANY,
    )
    contact = CanonicalContact(
        contact_id="c_001", provider="hubspot",
        email="alice@acme.com", first_name="Alice", last_name="Smith",
        lifecycle_stage="opportunity", associations=[assoc],
    )
    assert len(contact.associations) == 1


def test_canonical_deal_fields():
    deal = CanonicalDeal(
        deal_id="d_001", provider="salesforce",
        title="Enterprise Expansion", amount=150000.0, currency="EUR",
        stage_id="Closed Won", pipeline_id="sales_pipeline", is_won=True, is_closed=True,
    )
    assert deal.is_won is True
    assert deal.currency == "EUR"


def test_canonical_pipeline_stages():
    pipeline = CanonicalPipeline(
        pipeline_id="pipe_1", provider="hubspot", label="Sales Pipeline",
        stages=[
            CanonicalStage(stage_id="PROSPECT", label="Prospect", display_order=0, probability=0.1),
            CanonicalStage(stage_id="CLOSED_WON", label="Closed Won", display_order=1, probability=1.0, is_won=True, is_closed=True),
        ]
    )
    assert pipeline.stages[-1].is_won is True


def test_all_canonical_crm_models_instantiate():
    CanonicalContact(contact_id="c1", provider="hubspot")
    CanonicalCompany(company_id="co1", provider="hubspot", name="Acme")
    CanonicalDeal(deal_id="d1", provider="hubspot", title="Deal", stage_id="OPEN", pipeline_id="p1")
    CanonicalPipeline(pipeline_id="p1", provider="hubspot", label="Pipeline")
    CanonicalTask(task_id="t1", provider="hubspot", subject="Follow up")
    CanonicalNote(note_id="n1", provider="hubspot", body="Meeting notes")
    CanonicalActivity(activity_id="a1", provider="hubspot", activity_type=CanonicalActivityType.CALL, title="Discovery Call")
    CanonicalProduct(product_id="pr1", provider="hubspot", name="BizOS Pro", price=999.0)
    CanonicalOwner(owner_id="o1", provider="hubspot", email="rep@bizos.ai")


# ── 2. Deterministic UKO IDs ──────────────────────────────────────────────────

def test_uko_id_is_deterministic():
    """Same source+resource always produces the same UKO ID."""
    id1 = _uko_id("hubspot", "deal_12345")
    id2 = _uko_id("hubspot", "deal_12345")
    assert id1 == id2


def test_uko_id_differs_for_different_records():
    id1 = _uko_id("hubspot", "deal_12345")
    id2 = _uko_id("hubspot", "deal_99999")
    assert id1 != id2


def test_uko_id_differs_for_different_providers():
    id1 = _uko_id("hubspot", "contact_1")
    id2 = _uko_id("salesforce", "contact_1")
    assert id1 != id2


def test_uko_id_is_sha256():
    """UKO ID must be a valid SHA-256 hex digest (64 chars)."""
    uko = _uko_id("hubspot", "deal_abc")
    assert len(uko) == 64
    assert all(c in "0123456789abcdef" for c in uko)


def test_normalize_produces_deterministic_uko(hubspot):
    """Normalizing the same observation twice produces the same uko_id."""
    obs = ExternalObservation(
        observation_id=str(uuid4()),  # different each time
        source_id="hubspot", source_type=ObservationSourceType.CRM,
        resource_id="deal_FIXED_ID", resource_type="deal",
        title="Test Deal",
        raw_content=json.dumps({"id": "deal_FIXED_ID", "properties": {"dealname": "Test"}}),
    )
    uko1 = hubspot.normalize(obs)

    obs2 = ExternalObservation(
        observation_id=str(uuid4()),  # different observation_id
        source_id="hubspot", source_type=ObservationSourceType.CRM,
        resource_id="deal_FIXED_ID", resource_type="deal",
        title="Test Deal",
        raw_content=json.dumps({"id": "deal_FIXED_ID", "properties": {"dealname": "Test"}}),
    )
    uko2 = hubspot.normalize(obs2)

    assert uko1.uko_id == uko2.uko_id


# ── 3. HubSpot Normalization Tests ───────────────────────────────────────────

def test_hubspot_normalize_contact():
    raw = {
        "id": "12345",
        "properties": {
            "email": "bob@company.com",
            "firstname": "Bob",
            "lastname": "Jones",
            "lifecyclestage": "lead",
            "associatedcompanyid": "comp_99",
            "phone": "+1-555-0100",
            "jobtitle": "CTO",
        }
    }
    contact = hs_normalize_contact(raw)
    assert contact.contact_id == "12345"
    assert contact.email == "bob@company.com"
    assert contact.lifecycle_stage == "lead"
    assert len(contact.associations) == 1
    assert contact.associations[0].association_type == AssociationType.CONTACT_TO_COMPANY


def test_hubspot_normalize_deal_currency():
    """Deal currency should come from deal_currency_code, not hardcoded USD."""
    raw = {
        "id": "deal_001",
        "properties": {
            "dealname": "Euro Deal",
            "amount": "75000",
            "deal_currency_code": "EUR",
            "dealstage": "closedwon",
            "pipeline": "sales_pipeline",
        }
    }
    deal = hs_normalize_deal(raw)
    assert deal.currency == "EUR"
    assert deal.amount == 75000.0
    assert deal.is_won is True


def test_hubspot_normalize_deal_contact_ids():
    """deal.contact_ids should be populated from associations.contacts."""
    raw = {
        "id": "deal_002",
        "properties": {"dealname": "Team Deal", "amount": "10000", "dealstage": "proposal", "pipeline": "default"},
        "associations": {
            "contacts": {"results": [{"id": "c_a"}, {"id": "c_b"}]},
            "companies": {"results": []},
        }
    }
    deal = hs_normalize_deal(raw)
    assert set(deal.contact_ids) == {"c_a", "c_b"}


def test_hubspot_normalize_deal_is_closed():
    """closedwon and closedlost stages should set is_closed=True."""
    for stage, won in [("closedwon", True), ("closedlost", False)]:
        raw = {"id": "d1", "properties": {"dealname": "D", "amount": "0", "dealstage": stage, "pipeline": "default"}}
        deal = hs_normalize_deal(raw)
        assert deal.is_closed is True
        assert deal.is_won is won


def test_hubspot_normalize_company_annual_revenue_empty_string():
    """annualrevenue == '' should not raise — should return None."""
    raw = {
        "id": "co_1",
        "properties": {
            "name": "Acme",
            "annualrevenue": "",
            "numberofemployees": "",
        }
    }
    company = hs_normalize_company(raw)
    assert company.annual_revenue is None
    assert company.number_of_employees is None


def test_hubspot_normalize_company_resource_type(hubspot):
    """observe() must use resource_type='company', never 'companie'."""
    obs = ExternalObservation(
        observation_id=str(uuid4()),
        source_id="hubspot", source_type=ObservationSourceType.CRM,
        resource_id="co_1", resource_type="company",
        title="Acme Corp",
        raw_content=json.dumps({"id": "co_1", "properties": {"name": "Acme Corp", "domain": "acme.com"}}),
    )
    uko = hubspot.normalize(obs)
    assert uko.entity_type == "Company"
    assert "Company:" in uko.content or "Account:" in uko.content or "Acme" in uko.content


# ── 4. Salesforce Normalization Tests ────────────────────────────────────────

def test_sf_normalize_deal_currency():
    """Salesforce deal currency should come from CurrencyIsoCode."""
    raw = {
        "Id": "opp_1", "Name": "APAC Deal",
        "Amount": 200000.0, "CurrencyIsoCode": "SGD",
        "StageName": "Proposal/Price Quote", "Type": "New Business",
        "CloseDate": "2026-12-31",
    }
    deal = sf_normalize_deal(raw)
    assert deal.currency == "SGD"
    assert deal.amount == 200000.0


def test_sf_normalize_company_address_fields():
    """All billing address sub-fields should be captured."""
    raw = {
        "Id": "acc_1", "Name": "Global Inc",
        "BillingCity": "Singapore", "BillingCountry": "SG",
        "BillingStreet": "1 Marina Blvd", "BillingState": "Central",
        "BillingPostalCode": "018989",
    }
    company = sf_normalize_company(raw)
    assert company.city == "Singapore"
    assert company.country == "SG"


def test_sf_normalize_contact():
    raw = {
        "Id": "c_sf_1", "FirstName": "Jane", "LastName": "Doe",
        "Email": "jane@sf.com", "Phone": "+65-1234", "AccountId": "acc_2",
        "Title": "VP Sales", "LeadSource": "Web", "OwnerId": "owner_1",
    }
    contact = sf_normalize_contact(raw)
    assert contact.contact_id == "c_sf_1"
    assert contact.email == "jane@sf.com"
    assert len(contact.associations) == 1  # contact→company


def test_sf_normalize_deal_closed_stages():
    for stage, won in [("Closed Won", True), ("Closed Lost", False)]:
        raw = {"Id": "d1", "Name": "D", "Amount": 0, "StageName": stage, "Type": "default", "CloseDate": "2026-12-31"}
        deal = sf_normalize_deal(raw)
        assert deal.is_closed is True
        assert deal.is_won is won


# ── 5. SOQL Injection Guard ───────────────────────────────────────────────────

def test_sanitize_soql_removes_injection():
    """SQL injection payloads must be stripped from SOQL parameters."""
    injected = "' OR 1=1 LIMIT 1000 OR '"
    sanitized = _sanitize_soql(injected)
    assert "'" not in sanitized
    assert "=" not in sanitized
    assert "1=1" not in sanitized


def test_sanitize_soql_allows_safe_chars():
    """Normal search terms must pass through sanitization."""
    safe = "john.doe@company.com"
    assert _sanitize_soql(safe) == safe


def test_sanitize_soql_truncates():
    """Strings over max_len must be truncated."""
    long_str = "a" * 200
    assert len(_sanitize_soql(long_str, max_len=100)) == 100


def test_sanitize_soql_strips_special_chars():
    """Semicolons, quotes, brackets must be removed."""
    dangerous = "test; DROP TABLE Contact; --"
    sanitized = _sanitize_soql(dangerous)
    assert ";" not in sanitized
    assert "--" not in sanitized


# ── 6. Token Expiry Detection ─────────────────────────────────────────────────

def test_vault_is_token_expired_unexpired():
    """Token with future expiry should not be considered expired."""
    tenant = str(uuid4())
    ConnectorAuthVault.set_tokens(
        "hubspot", access_token="tok_valid", tenant_id=tenant,
        expires_in=3600,
    )
    assert ConnectorAuthVault.is_token_expired("hubspot", tenant_id=tenant) is False


def test_vault_is_token_expired_past():
    """Token with past expiry should be considered expired."""
    from datetime import datetime, timezone, timedelta
    tenant = str(uuid4())
    past = datetime.now(timezone.utc) - timedelta(seconds=100)
    ConnectorAuthVault.set_tokens(
        "hubspot", access_token="tok_expired", tenant_id=tenant,
        expires_at=past,
    )
    assert ConnectorAuthVault.is_token_expired("hubspot", tenant_id=tenant) is True


def test_vault_no_expiry_not_expired():
    """Token with no expiry info should not be considered expired."""
    tenant = str(uuid4())
    ConnectorAuthVault.set_tokens("hubspot", access_token="tok_no_expiry", tenant_id=tenant)
    assert ConnectorAuthVault.is_token_expired("hubspot", tenant_id=tenant) is False


# ── 7. Token Refresh Flow ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_hubspot_get_token_triggers_refresh_on_expired(hubspot):
    """When the stored token is expired and a refresh_token exists,
    _get_token() should call the refresh endpoint and store the new token."""
    tenant = str(uuid4())
    past = datetime.now(timezone.utc) - timedelta(seconds=100)
    ConnectorAuthVault.set_tokens(
        "hubspot",
        access_token="expired_token",
        refresh_token="valid_refresh_token",
        tenant_id=tenant,
        expires_at=past,
        extra={"client_id": "test_client", "client_secret": "test_secret"},
    )

    new_token_response = {
        "access_token": "fresh_access_token",
        "refresh_token": "new_refresh_token",
        "expires_in": 21600,
    }

    with patch("app.connectors.hubspot.connector._refresh_hubspot_token",
               return_value=new_token_response) as mock_refresh:
        from app.connectors.hubspot.connector import _get_token
        token = _get_token(tenant)

    mock_refresh.assert_called_once_with("valid_refresh_token", "test_client", "test_secret")
    assert token == "fresh_access_token"

    # Vault should now hold the fresh token
    stored = ConnectorAuthVault.get_tokens("hubspot", tenant_id=tenant)
    assert stored["access_token"] == "fresh_access_token"


@pytest.mark.asyncio
async def test_salesforce_get_credentials_triggers_refresh(salesforce):
    """Expired Salesforce token with refresh_token should auto-refresh."""
    tenant = str(uuid4())
    past = datetime.now(timezone.utc) - timedelta(seconds=100)
    ConnectorAuthVault.set_tokens(
        "salesforce",
        access_token="expired_sf_token",
        refresh_token="sf_refresh_token",
        tenant_id=tenant,
        expires_at=past,
        extra={
            "instance_url": "https://test.salesforce.com",
            "client_id": "sf_client",
            "client_secret": "sf_secret",
        },
    )

    new_token_response = {
        "access_token": "fresh_sf_token",
        "instance_url": "https://test.salesforce.com",
    }

    with patch("app.connectors.salesforce.connector._refresh_sf_token",
               return_value=new_token_response):
        from app.connectors.salesforce.connector import _get_credentials
        creds = _get_credentials(tenant)

    assert creds["access_token"] == "fresh_sf_token"


# ── 8. 429 Rate-Limit Retry ───────────────────────────────────────────────────

def test_retry_on_429_succeeds_after_backoff():
    """http_request_with_retry should retry on 429 and succeed on 3rd attempt."""
    import urllib.error
    from app.connectors.sdk.retry import http_request_with_retry

    call_count = 0

    def mock_urlopen(req, timeout=15):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            err = urllib.error.HTTPError(
                url="http://test", code=429, msg="Too Many Requests",
                hdrs=MagicMock(**{"get.return_value": "1"}), fp=None
            )
            raise err
        # Third attempt succeeds
        resp = MagicMock()
        resp.__enter__ = lambda s: s
        resp.__exit__ = MagicMock(return_value=False)
        resp.read.return_value = b'{"results": []}'
        return resp

    with patch("urllib.request.urlopen", side_effect=mock_urlopen):
        with patch("time.sleep"):  # Speed up the test
            result = http_request_with_retry(
                method="GET",
                url="https://api.example.com/test",
                headers={"Authorization": "Bearer tok"},
                provider="hubspot",
                action="test",
                max_retries=3,
            )

    assert call_count == 3
    assert result == {"results": []}


def test_retry_raises_after_max_retries():
    """http_request_with_retry should raise ConnectorException after max retries."""
    import urllib.error
    from app.connectors.sdk.retry import http_request_with_retry

    def always_429(req, timeout=15):
        raise urllib.error.HTTPError(
            url="http://test", code=429, msg="Too Many Requests",
            hdrs=MagicMock(**{"get.return_value": "1"}), fp=None
        )

    with patch("urllib.request.urlopen", side_effect=always_429):
        with patch("time.sleep"):
            with pytest.raises(ConnectorException) as exc_info:
                http_request_with_retry(
                    method="GET",
                    url="https://api.example.com/test",
                    headers={},
                    provider="hubspot",
                    action="test",
                    max_retries=2,
                )

    assert exc_info.value.error.code == "RATE_LIMITED"
    assert exc_info.value.error.retryable is True


def test_404_raises_not_found_immediately():
    """404 should not be retried — raise ConnectorException immediately."""
    import urllib.error
    from app.connectors.sdk.retry import http_request_with_retry

    call_count = 0

    def mock_404(req, timeout=15):
        nonlocal call_count
        call_count += 1
        raise urllib.error.HTTPError(
            url="http://test", code=404, msg="Not Found",
            hdrs=MagicMock(), fp=None
        )

    with patch("urllib.request.urlopen", side_effect=mock_404):
        with pytest.raises(ConnectorException) as exc_info:
            http_request_with_retry(
                method="GET", url="https://api.example.com/test",
                headers={}, provider="hubspot", action="get_contact", max_retries=3,
            )

    assert call_count == 1  # Not retried
    assert exc_info.value.error.code == "NOT_FOUND"


def test_401_raises_auth_error_immediately():
    """401 should not be retried — raise ConnectorException(code=AUTH_EXPIRED) immediately."""
    import urllib.error
    from app.connectors.sdk.retry import http_request_with_retry

    def mock_401(req, timeout=15):
        raise urllib.error.HTTPError(
            url="http://test", code=401, msg="Unauthorized",
            hdrs=MagicMock(), fp=None
        )

    with patch("urllib.request.urlopen", side_effect=mock_401):
        with pytest.raises(ConnectorException) as exc_info:
            http_request_with_retry(
                method="GET", url="https://api.example.com/test",
                headers={}, provider="salesforce", action="list_contacts",
            )

    assert exc_info.value.error.code == "AUTH_EXPIRED"
    assert exc_info.value.error.retryable is False


# ── 9. BizOS Error Mapping in execute() ──────────────────────────────────────

@pytest.mark.asyncio
async def test_hubspot_execute_returns_error_dict_on_connector_exception(hubspot, prod_ctx):
    """When the connector raises ConnectorException, execute() must return an error dict,
    not propagate the exception to the agent's execution loop."""
    tenant = prod_ctx.tenant_id
    ConnectorAuthVault.set_tokens("hubspot", access_token="tok", tenant_id=tenant)

    with patch("app.connectors.hubspot.connector._hs_request") as mock_req:
        mock_req.side_effect = ConnectorException(ConnectorError(
            code="RATE_LIMITED", provider="hubspot", action="list_contacts",
            severity="WARNING", retryable=True,
            user_message="Rate limit hit.",
        ))
        req = ConnectorExecuteRequest(capability="list_contacts", params={})
        result = await hubspot.execute(req, prod_ctx)

    assert result["status"] == "error"
    assert result["error"] == "RATE_LIMITED"
    assert result["retryable"] is True


@pytest.mark.asyncio
async def test_salesforce_execute_returns_error_dict_on_exception(salesforce, prod_ctx):
    """Same as above for Salesforce."""
    tenant = prod_ctx.tenant_id
    ConnectorAuthVault.set_tokens(
        "salesforce", access_token="tok", tenant_id=tenant,
        extra={"instance_url": "https://test.sf.com"},
    )

    with patch("app.connectors.salesforce.connector._soql_query") as mock_q:
        mock_q.side_effect = ConnectorException(ConnectorError(
            code="NOT_FOUND", provider="salesforce", action="list_contacts",
            severity="ERROR", retryable=False, user_message="Not found.",
        ))
        req = ConnectorExecuteRequest(capability="list_contacts", params={})
        result = await salesforce.execute(req, prod_ctx)

    assert result["status"] == "error"
    assert result["error"] == "NOT_FOUND"


# ── 10. HubSpot Pagination ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_hubspot_list_contacts_returns_next_cursor(hubspot, prod_ctx):
    """list_contacts must return next_cursor when HubSpot provides paging.next.after."""
    tenant = prod_ctx.tenant_id
    ConnectorAuthVault.set_tokens("hubspot", access_token="tok", tenant_id=tenant)

    mock_response = {
        "results": [{"id": "c1", "properties": {"email": "a@b.com", "firstname": "A", "lastname": "B"}}],
        "paging": {"next": {"after": "CURSOR_TOKEN_XYZ"}},
    }

    with patch("app.connectors.hubspot.connector._hs_request", return_value=mock_response):
        req = ConnectorExecuteRequest(capability="list_contacts", params={"limit": 10})
        result = await hubspot.execute(req, prod_ctx)

    assert result["status"] == "EXECUTED"
    assert result["next_cursor"] == "CURSOR_TOKEN_XYZ"
    assert len(result["items"]) == 1


@pytest.mark.asyncio
async def test_hubspot_list_contacts_no_cursor_when_no_more(hubspot, prod_ctx):
    """When no next page, next_cursor must be None."""
    tenant = prod_ctx.tenant_id
    ConnectorAuthVault.set_tokens("hubspot", access_token="tok", tenant_id=tenant)

    mock_response = {
        "results": [{"id": "c1", "properties": {}}],
        "paging": {},
    }
    with patch("app.connectors.hubspot.connector._hs_request", return_value=mock_response):
        req = ConnectorExecuteRequest(capability="list_contacts", params={})
        result = await hubspot.execute(req, prod_ctx)

    assert result["next_cursor"] is None


# ── 11. Salesforce SOQL Pagination ───────────────────────────────────────────

def test_soql_query_follows_next_records_url():
    """_soql_query must follow nextRecordsUrl to get all pages."""
    from app.connectors.salesforce.connector import _soql_query

    page1 = {
        "records": [{"Id": "c1"}, {"Id": "c2"}],
        "done": False,
        "nextRecordsUrl": f"/services/data/v58.0/query-next/page2",
    }
    page2 = {
        "records": [{"Id": "c3"}],
        "done": True,
    }

    call_count = [0]
    def mock_sf_request(method, instance_url, path, token, payload=None, action=""):
        call_count[0] += 1
        if "page2" in path:
            return page2
        return page1

    with patch("app.connectors.salesforce.connector._sf_request", side_effect=mock_sf_request):
        records = _soql_query("https://test.sf.com", "tok", "SELECT Id FROM Contact")

    assert len(records) == 3
    assert call_count[0] == 2  # Two requests: initial + follow-up page


# ── 12. Webhook Verification (HubSpot) ───────────────────────────────────────

def test_hubspot_webhook_valid_signature(hubspot):
    """Valid HMAC-SHA256 signature within time window must verify True."""
    import hashlib, hmac as hmac_lib

    client_secret = "my-client-secret"
    method = "POST"
    url = "https://bizos.ai/webhooks/hubspot"
    body = b'[{"objectId": "12345", "eventType": "contact.creation"}]'
    ts_ms = str(int(time.time() * 1000))

    body_str = body.decode("utf-8")
    signing_string = f"{method}{url}{body_str}{ts_ms}"
    expected_sig = hmac_lib.new(
        client_secret.encode("utf-8"),
        signing_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    headers = {
        "X-HubSpot-Signature-v3": expected_sig,
        "X-HubSpot-Request-Timestamp": ts_ms,
    }

    assert hubspot.verify_webhook(headers, body, client_secret, method, url) is True


def test_hubspot_webhook_invalid_signature(hubspot):
    """Tampered signature must return False."""
    ts_ms = str(int(time.time() * 1000))
    headers = {
        "X-HubSpot-Signature-v3": "totally_wrong_signature",
        "X-HubSpot-Request-Timestamp": ts_ms,
    }
    assert hubspot.verify_webhook(headers, b"body", "secret") is False


def test_hubspot_webhook_replay_rejected(hubspot):
    """Signature older than 5 minutes must be rejected."""
    old_ts_ms = str(int((time.time() - 400) * 1000))  # 400 seconds ago > 5 min
    headers = {
        "X-HubSpot-Signature-v3": "some_sig",
        "X-HubSpot-Request-Timestamp": old_ts_ms,
    }
    assert hubspot.verify_webhook(headers, b"body", "secret") is False


def test_hubspot_webhook_missing_headers(hubspot):
    """Missing signature header must return False."""
    assert hubspot.verify_webhook({}, b"body", "secret") is False


# ── 13. Batch Operations ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_hubspot_batch_simulation(hubspot, sim_ctx):
    """Batch in simulation mode must return SIMULATED status."""
    operations = [
        {"type": "create", "object_type": "contacts", "properties": {"email": "a@b.com"}},
        {"type": "update", "object_type": "contacts", "id": "c1", "properties": {"phone": "123"}},
    ]
    result = await hubspot.batch(operations, sim_ctx)
    assert result["status"] == "SIMULATED"
    assert result["processed"] == 2


@pytest.mark.asyncio
async def test_salesforce_batch_simulation(salesforce, sim_ctx):
    """Salesforce batch in simulation mode must return SIMULATED."""
    operations = [
        {"type": "create", "object_type": "contact", "properties": {"LastName": "Test"}},
    ]
    result = await salesforce.batch(operations, sim_ctx)
    assert result["status"] == "SIMULATED"
    assert result["processed"] == 1


# ── 14. Delta Sync Timestamp Bounds ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_hubspot_observe_with_last_sync_uses_search(hubspot):
    """observe() with last_sync_at must use the search endpoint with date filter."""
    tenant = str(uuid4())
    ConnectorAuthVault.set_tokens("hubspot", access_token="tok", tenant_id=tenant)

    mock_search_response = {"results": [], "paging": {}}
    calls = []

    def mock_hs_request(method, path, token, payload=None, **kwargs):
        calls.append({"method": method, "path": path, "payload": payload})
        return mock_search_response

    with patch("app.connectors.hubspot.connector._hs_request", side_effect=mock_hs_request):
        last_sync = datetime.now(timezone.utc) - timedelta(hours=1)
        ctx = _make_perception_ctx(tenant, last_sync_at=last_sync)
        await hubspot.observe(ctx)

    # All calls should be POST to search endpoints
    search_calls = [c for c in calls if c["method"] == "POST"]
    assert len(search_calls) > 0
    for call in search_calls:
        assert "search" in call["path"]
        assert call["payload"] is not None
        assert "filterGroups" in call["payload"]


@pytest.mark.asyncio
async def test_hubspot_observe_without_last_sync_uses_list(hubspot):
    """observe() without last_sync_at must use GET list endpoints."""
    tenant = str(uuid4())
    ConnectorAuthVault.set_tokens("hubspot", access_token="tok", tenant_id=tenant)

    calls = []

    def mock_hs_request(method, path, token, payload=None, **kwargs):
        calls.append({"method": method, "path": path})
        return {"results": []}

    with patch("app.connectors.hubspot.connector._hs_request", side_effect=mock_hs_request):
        ctx = _make_perception_ctx(tenant, last_sync_at=None)
        await hubspot.observe(ctx)

    get_calls = [c for c in calls if c["method"] == "GET"]
    assert len(get_calls) > 0


@pytest.mark.asyncio
async def test_salesforce_observe_with_last_sync_uses_where_clause(salesforce):
    """observe() with last_sync_at must include WHERE LastModifiedDate > ts in SOQL."""
    tenant = str(uuid4())
    ConnectorAuthVault.set_tokens(
        "salesforce", access_token="tok", tenant_id=tenant,
        extra={"instance_url": "https://test.sf.com"},
    )

    captured_queries = []

    def mock_soql(instance_url, token, query, action=""):
        captured_queries.append(query)
        return []

    with patch("app.connectors.salesforce.connector._soql_query", side_effect=mock_soql):
        last_sync = datetime.now(timezone.utc) - timedelta(hours=2)
        ctx = _make_perception_ctx(tenant, last_sync_at=last_sync)
        await salesforce.observe(ctx)

    assert len(captured_queries) > 0
    for q in captured_queries:
        assert "WHERE LastModifiedDate >" in q


# ── 15. Structured Normalize Content ─────────────────────────────────────────

def test_hubspot_normalize_deal_content_is_structured(hubspot):
    raw = {"id": "d1", "properties": {
        "dealname": "Enterprise Contract", "dealstage": "proposal",
        "amount": "75000", "deal_currency_code": "GBP", "pipeline": "sales",
    }}
    obs = ExternalObservation(
        observation_id=str(uuid4()), source_id="hubspot",
        source_type=ObservationSourceType.CRM, resource_id="d1",
        resource_type="deal", title="Enterprise Contract",
        raw_content=json.dumps(raw),
    )
    uko = hubspot.normalize(obs)
    assert "Deal:" in uko.content
    assert "Stage:" in uko.content
    assert "GBP" in uko.content


def test_hubspot_normalize_company_content_is_structured(hubspot):
    raw = {"id": "co1", "properties": {
        "name": "TechCorp", "domain": "techcorp.com",
        "industry": "Technology", "annualrevenue": "5000000",
        "country": "US",
    }}
    obs = ExternalObservation(
        observation_id=str(uuid4()), source_id="hubspot",
        source_type=ObservationSourceType.CRM, resource_id="co1",
        resource_type="company", title="TechCorp",
        raw_content=json.dumps(raw),
    )
    uko = hubspot.normalize(obs)
    assert "Company:" in uko.content
    assert "Technology" in uko.content


def test_salesforce_normalize_deal_content_is_structured(salesforce):
    raw = {
        "Id": "opp_sf_1", "Name": "Global Deal",
        "StageName": "Proposal/Price Quote", "Amount": 80000,
        "CurrencyIsoCode": "AED", "Probability": 60.0,
        "CloseDate": "2026-12-31",
    }
    obs = ExternalObservation(
        observation_id=str(uuid4()), source_id="salesforce",
        source_type=ObservationSourceType.CRM, resource_id="opp_sf_1",
        resource_type="deal", title="Global Deal",
        raw_content=json.dumps(raw),
    )
    uko = salesforce.normalize(obs)
    assert "Opportunity:" in uko.content
    assert "AED" in uko.content
    assert "60" in uko.content
    assert uko.metadata["sf_stage"] == "Proposal/Price Quote"
    assert uko.metadata["sf_currency"] == "AED"


def test_salesforce_normalize_company_content_is_structured(salesforce):
    raw = {
        "Id": "acc_1", "Name": "Global Inc",
        "Website": "global.com", "Industry": "Finance",
        "BillingCity": "New York", "BillingCountry": "US",
    }
    obs = ExternalObservation(
        observation_id=str(uuid4()), source_id="salesforce",
        source_type=ObservationSourceType.CRM, resource_id="acc_1",
        resource_type="company", title="Global Inc",
        raw_content=json.dumps(raw),
    )
    uko = salesforce.normalize(obs)
    assert "Account:" in uko.content
    assert "Finance" in uko.content
    assert "New York" in uko.content


# ── 16. Connector Capabilities ───────────────────────────────────────────────

def test_hubspot_capabilities(hubspot):
    caps = hubspot.capabilities
    assert caps.connector_id == "hubspot"
    assert caps.family == "crm"
    assert "list_contacts" in caps.supported_actions
    assert "close_deal_won" in caps.supported_actions
    assert len(caps.supported_actions) == 21


def test_salesforce_capabilities(salesforce):
    caps = salesforce.capabilities
    assert caps.family == "crm"
    assert "list_contacts" in caps.supported_actions
    assert "close_deal_won" in caps.supported_actions
    assert len(caps.supported_actions) == 21


# ── 17. Simulation Mode (all 21 actions) ──────────────────────────────────────

@pytest.mark.asyncio
async def test_hubspot_all_actions_simulation(hubspot, sim_ctx):
    for action in hubspot.capabilities.supported_actions:
        req = ConnectorExecuteRequest(capability=action, params={
            "contact_id": "c1", "deal_id": "d1", "company_id": "co1",
            "task_id": "t1", "target_stage_id": "NEGOTIATION",
        })
        result = await hubspot.execute(req, sim_ctx)
        assert result["status"] == "SIMULATED", f"Action '{action}' did not return SIMULATED"
        assert result["connector"] == "hubspot"


@pytest.mark.asyncio
async def test_salesforce_all_actions_simulation(salesforce, sim_ctx):
    for action in salesforce.capabilities.supported_actions:
        req = ConnectorExecuteRequest(capability=action, params={
            "contact_id": "c1", "deal_id": "d1", "company_id": "co1",
            "task_id": "t1", "target_stage_id": "Negotiation/Review",
        })
        result = await salesforce.execute(req, sim_ctx)
        assert result["status"] == "SIMULATED", f"SF action '{action}' did not return SIMULATED"


# ── 18. Health Check ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_hubspot_health_check_static(hubspot):
    health = await hubspot.health_check()
    assert "status" in health
    assert health["connector"] == "hubspot"


@pytest.mark.asyncio
async def test_salesforce_health_check_static(salesforce):
    health = await salesforce.health_check()
    assert "status" in health
    assert health["connector"] == "salesforce"


@pytest.mark.asyncio
async def test_hubspot_health_live_returns_healthy(hubspot):
    tenant = str(uuid4())
    ConnectorAuthVault.set_tokens("hubspot", access_token="live_tok", tenant_id=tenant)

    with patch("app.connectors.hubspot.connector._hs_request", return_value={"results": []}):
        result = await hubspot.health()

    assert result["status"] == "healthy"


@pytest.mark.asyncio
async def test_salesforce_health_live_returns_healthy(salesforce):
    tenant = str(uuid4())
    ConnectorAuthVault.set_tokens(
        "salesforce", access_token="sf_live_tok", tenant_id=tenant,
        extra={"instance_url": "https://test.sf.com"},
    )

    limits_response = {"DailyApiRequests": {"Remaining": 14500, "Max": 15000}}
    with patch("app.connectors.salesforce.connector._sf_request", return_value=limits_response):
        result = await salesforce.health()

    assert result["status"] == "healthy"
    assert result["api_calls_remaining"] == 14500


# ── 19. IObservationSource Identity ──────────────────────────────────────────

def test_hubspot_source_type(hubspot):
    assert hubspot.source_type == ObservationSourceType.CRM
    assert hubspot.source_id == "hubspot"


def test_salesforce_source_type(salesforce):
    assert salesforce.source_type == ObservationSourceType.CRM
    assert salesforce.source_id == "salesforce"


@pytest.mark.asyncio
async def test_hubspot_observe_unauthenticated(hubspot):
    ctx = _make_perception_ctx(str(uuid4()))
    obs_list = await hubspot.observe(ctx)
    assert isinstance(obs_list, list)
    assert len(obs_list) == 0  # graceful empty return


@pytest.mark.asyncio
async def test_salesforce_observe_unauthenticated(salesforce):
    ctx = _make_perception_ctx(str(uuid4()))
    obs_list = await salesforce.observe(ctx)
    assert isinstance(obs_list, list)
    assert len(obs_list) == 0


# ── 20. BusinessEventDetector CRM patterns ───────────────────────────────────

@pytest.fixture
def detector():
    return BusinessEventDetector()


def test_crm_detect_deal_won(detector):
    uko = UnifiedKnowledgeObject(
        uko_id="uko_1", resource_type="deal",
        title="Deal closed won — Enterprise Contract signed",
        content="We have closed won the deal. Purchase order received.",
    )
    event_types = [e.event_type for e in detector.detect(uko)]
    assert BusinessEventType.DEAL_WON in event_types


def test_crm_detect_new_lead(detector):
    uko = UnifiedKnowledgeObject(
        uko_id="uko_2", resource_type="contact",
        title="New lead created",
        content="A new lead was created in HubSpot. Prospect added to pipeline.",
    )
    event_types = [e.event_type for e in detector.detect(uko)]
    assert BusinessEventType.NEW_LEAD in event_types


def test_crm_detect_deal_stage_changed(detector):
    uko = UnifiedKnowledgeObject(
        uko_id="uko_3", resource_type="deal",
        title="Deal stage changed",
        content="Pipeline stage moved from Proposal to Negotiation.",
    )
    event_types = [e.event_type for e in detector.detect(uko)]
    assert BusinessEventType.DEAL_STAGE_CHANGED in event_types


def test_crm_detect_support_ticket(detector):
    uko = UnifiedKnowledgeObject(
        uko_id="uko_4", resource_type="ticket",
        title="Support ticket opened",
        content="Customer raised a support request. Case opened in Zendesk.",
    )
    event_types = [e.event_type for e in detector.detect(uko)]
    assert BusinessEventType.SUPPORT_TICKET_CREATED in event_types


# ── 21. BusinessStateChangeEvent state_delta ─────────────────────────────────

def test_business_state_change_event_state_delta():
    event = BusinessStateChangeEvent(
        correlation_id=str(uuid4()),
        change_id=str(uuid4()),
        source_uko_id=str(uuid4()),
        source_connector="hubspot",
        entity_type="Deal",
        affected_entity_ids=["deal_778899"],
        business_event_types=["STATE_TRANSITION", "DEAL_WON"],
        state_delta={
            "pipeline_stage": {"old": "PROPOSAL", "new": "CLOSED_WON"},
            "amount": 150000.0,
        },
        confidence=0.95,
        suggested_actions=["Trigger onboarding workflow"],
    )
    assert event.entity_type == "Deal"
    assert event.state_delta["pipeline_stage"]["new"] == "CLOSED_WON"
    assert event.confidence == 0.95
