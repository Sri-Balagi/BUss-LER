"""Unit tests for BizOS External Connectors (Gmail, WhatsApp, Instagram, Google Drive, Banking & UPI)"""

import pytest
from uuid import uuid4
from app.connectors.gmail.connector import GmailConnector
from app.connectors.whatsapp.connector import WhatsAppConnector
from app.connectors.instagram.connector import InstagramConnector
from app.connectors.google_drive.connector import GoogleDriveConnector
from app.connectors.banking_upi.connector import BankingUPIConnector
from app.domain.shared.context import ExecutionContext
from app.shared.enums import ExecutionMode


@pytest.mark.asyncio
async def test_all_connectors_execution_and_health():
    ctx_sim = ExecutionContext(
        tenant_id=str(uuid4()),
        principal_id="user_123",
        session_id=str(uuid4()),
        conversation_id=str(uuid4()),
        trace_id=str(uuid4()),
        correlation_id=str(uuid4()),
        execution_mode=ExecutionMode.SIMULATION,
    )
    ctx_prod = ExecutionContext(
        tenant_id=str(uuid4()),
        principal_id="user_123",
        session_id=str(uuid4()),
        conversation_id=str(uuid4()),
        trace_id=str(uuid4()),
        correlation_id=str(uuid4()),
        execution_mode=ExecutionMode.PRODUCTION,
    )

    connectors = [
        GmailConnector(),
        WhatsAppConnector(),
        InstagramConnector(),
        GoogleDriveConnector(),
        BankingUPIConnector(),
    ]

    for conn in connectors:
        # Test capabilities
        caps = conn.capabilities
        assert caps.connector_id == conn.connector_id
        assert len(caps.supported_actions) > 0

        # Test health check
        health = await conn.health_check()
        h_status = str(health.get("status", "")).lower()
        assert h_status in [
            "healthy",
            "ok",
            "unconfigured",
            "authentication_required",
            "connectorhealthstatus.healthy",
            "connectorhealthstatus.authentication_required",
        ]

        # Test simulation mode
        action = caps.supported_actions[0]
        sim_res = await conn.execute_action(action, {"sample": "data"}, ctx_sim)
        assert sim_res["status"] in ["SIMULATED", "EXECUTED", "ok", "SUCCESS"]
        assert sim_res["connector"] in [conn.connector_id, "open_banking"]

        # Test production mode
        prod_res = await conn.execute_action(action, {"sample": "data"}, ctx_prod)
        assert prod_res["status"] in ["SIMULATED", "EXECUTED", "ok", "SUCCESS"]
        assert prod_res["connector"] in [conn.connector_id, "open_banking"]
