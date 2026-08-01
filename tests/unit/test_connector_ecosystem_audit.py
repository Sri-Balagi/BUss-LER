"""End-to-End Audit & Verification Test Suite for BizOS Connector Ecosystem

Verifies:
  - Single Google OAuth Consent Flow (Gmail + Drive)
  - WhatsApp Phone Verification & Consent Flow
  - Optional Instagram Business Connection
  - Provider-Based Financial Authentication Framework (OpenBanking, AccountAggregator, Stripe, Razorpay)
  - Auto-Discovery & Account Selection Flow
  - Zero Password/PIN storage verification
  - All 11 Core Platform Integration Requirements across all connectors
"""

import pytest
from app.connectors.auth.vault import ConnectorAuthVault
from app.connectors.auditor.integration_engine import ConnectorAuditor
from app.connectors.banking_upi.connector import BankingUPIConnector


@pytest.mark.asyncio
async def test_google_unified_oauth_consent_flow():
    vault = ConnectorAuthVault()
    user_id = "user_google_123"

    scopes = [
        "https://www.googleapis.com/auth/gmail.modify",
        "https://www.googleapis.com/auth/drive.file",
    ]

    res = await vault.register_google_unified_auth(user_id, "auth_code_xyz", scopes)
    assert res["status"] == "SUCCESS"
    assert res["connected_services"]["gmail"] is True
    assert res["connected_services"]["google_drive"] is True

    gmail_cred = await vault.get_credential(user_id, "google")
    assert gmail_cred is not None
    assert gmail_cred.metadata["gmail_connected"] is True
    assert gmail_cred.metadata["drive_connected"] is True


@pytest.mark.asyncio
async def test_whatsapp_phone_verification_consent_flow():
    vault = ConnectorAuthVault()
    user_id = "user_wa_456"

    res = await vault.register_whatsapp_auth(user_id, "+15550199", otp_verified=True)
    assert res["status"] == "SUCCESS"
    assert res["service"] == "whatsapp"

    cred = await vault.get_credential(user_id, "whatsapp")
    assert cred is not None
    assert cred.metadata["verified"] is True


@pytest.mark.asyncio
async def test_instagram_optional_connection_flow():
    vault = ConnectorAuthVault()
    user_id = "user_ig_789"

    res = await vault.register_instagram_optional_auth(user_id, "ig_biz_112233", "token_abc")
    assert res["status"] == "SUCCESS"

    cred = await vault.get_credential(user_id, "instagram")
    assert cred is not None
    assert cred.metadata["optional_connected"] is True


@pytest.mark.asyncio
async def test_financial_provider_strategy_framework_and_auto_discovery():
    connector = BankingUPIConnector()
    user_id = "user_fin_999"

    providers_to_test = ["open_banking", "account_aggregator", "stripe", "razorpay"]

    for pid in providers_to_test:
        # 1. Initiate Provider Auth (Returns Auth URL without manual password/PIN entry)
        init_res = await connector.initiate_provider_auth(user_id, pid)
        assert init_res["status"] == "INITIATED"
        assert init_res["requires_manual_credentials"] is False
        assert "auth_url" in init_res

        # 2. Complete Provider Auth (Exchanges auth payload for tokens)
        comp_res = await connector.complete_provider_auth(pid, {"code": f"test_code_{pid}"})
        assert comp_res["status"] == "SUCCESS"
        assert "access_token" in comp_res

        # 3. Auto-Discover Available Accounts
        accounts = await connector.discover_provider_accounts(pid, comp_res["access_token"])
        assert len(accounts) > 0
        assert accounts[0].provider_id == pid
        assert "****" in accounts[0].masked_identifier or "@" in accounts[0].masked_identifier or "acct_" in accounts[0].masked_identifier


@pytest.mark.asyncio
async def test_connector_ecosystem_full_auditor():
    auditor = ConnectorAuditor()
    reports = await auditor.run_full_ecosystem_audit()

    assert len(reports) == 5
    for rep in reports:
        assert rep["all_passed"] is True, f"Connector {rep['connector_id']} failed audit: {rep['details']}"
