"""Unit Test Suite for BizOS Phase 1 Connector Ecosystem"""

import pytest
import uuid
from datetime import datetime, timezone

from app.connectors.auth.vault import ConnectorAuthVault
from app.connectors.sdk.permissions import ConnectorPermission
from app.connectors.sdk.session import ConnectorSessionManager
from app.connectors.sdk.registry.capability_registry import ConnectorCapabilityRegistry
from app.connectors.sdk.doc_generator import ConnectorDocGenerator
from app.connectors.sdk.quota import ProviderQuotaTracker
from app.connectors.runtime.bridge import UniversalConnectorRuntimeBridge
from app.connectors.runtime.analytics import ConnectorAnalyticsTracker
from app.connectors.google_workspace.connector import GoogleWorkspaceConnector
from app.connectors.gmail.connector import GmailConnector
from app.connectors.google_drive.connector import GoogleDriveConnector
from app.connectors.google_calendar.connector import GoogleCalendarConnector
from app.connectors.banking_upi.connector import BankingUPIConnector
from app.connectors.banking_upi.providers.stripe_connect import StripeConnectProvider
from app.connectors.banking_upi.providers.razorpay import RazorpayProvider
from app.connectors.banking_upi.providers.open_banking import OpenBankingProvider
from app.domain.shared.context import ExecutionContext
from app.shared.enums import ExecutionMode


@pytest.fixture(autouse=True)
def setup_connectors():
    gw = GoogleWorkspaceConnector()
    gmail = GmailConnector()
    drive = GoogleDriveConnector()
    calendar = GoogleCalendarConnector()
    gw.register_child_connector(gmail)
    gw.register_child_connector(drive)
    gw.register_child_connector(calendar)

    banking = BankingUPIConnector()
    stripe = StripeConnectProvider()
    razorpay = RazorpayProvider()
    open_banking = OpenBankingProvider()

    for c in [gw, gmail, drive, calendar, banking, stripe, razorpay, open_banking]:
        ConnectorCapabilityRegistry.register_connector(c)


@pytest.mark.asyncio
async def test_capability_registry():
    capabilities = ConnectorCapabilityRegistry.list_all_capabilities()
    assert "send_email" in capabilities
    assert "upload_file" in capabilities
    assert "check_balance" in capabilities
    assert "fetch_bank_statement" in capabilities


@pytest.mark.asyncio
async def test_gmail_connector_execution():
    gmail = GmailConnector()
    context = ExecutionContext(
        tenant_id="test_tenant",
        execution_mode=ExecutionMode.PRODUCTION,
        principal_id="test_user",
        session_id="sess_123",
        correlation_id="corr_123",
        conversation_id="conv_123",
        trace_id="trace_123",
    )
    res = await UniversalConnectorRuntimeBridge.execute(
        connector=gmail,
        action="send_email",
        params={"to": "test@example.com", "subject": "Test", "body": "Hello"},
        context=context,
    )
    assert "canonical_email" in res
    assert res["canonical_email"]["subject"] == "Test"


@pytest.mark.asyncio
async def test_stripe_connector_execution():
    stripe = StripeConnectProvider()
    context = ExecutionContext(
        tenant_id="test_tenant",
        execution_mode=ExecutionMode.PRODUCTION,
        principal_id="test_user",
        session_id="sess_123",
        correlation_id="corr_123",
        conversation_id="conv_123",
        trace_id="trace_123",
    )
    res = await UniversalConnectorRuntimeBridge.execute(
        connector=stripe,
        action="check_balance",
        params={"sandbox": True},
        context=context,
    )
    assert "canonical_account" in res
    assert res["canonical_account"]["currency"] == "USD"


@pytest.mark.asyncio
async def test_quota_tracker():
    q = ProviderQuotaTracker.record_api_call("google_workspace", cost=10, daily_limit=1000)
    assert q.daily_usage == 10
    assert q.remaining_quota == 990
    assert q.consumption_pct == 1.0


@pytest.mark.asyncio
async def test_doc_generator():
    gmail = GmailConnector()
    docs = ConnectorDocGenerator.generate_markdown_docs(gmail)
    assert "Gmail Connector Documentation" in docs
    assert "send_email" in docs
