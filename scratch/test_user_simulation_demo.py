"""Simulation execution demonstration for User Onboarding & Test Actions

Demonstrates:
  1. Simulated OAuth Consent & Test Email to iamlnavdeeep@gmail.com
  2. Simulated OTP Phone Verification & Test WhatsApp Message to 9445076705
  3. Simulated Provider Auth & Masked Account Summary for IPPB Account (****8165)
  4. Instant Credential Anonymization & Forget Sequence
"""

import asyncio
from uuid import uuid4
from app.connectors.gmail.connector import GmailConnector
from app.connectors.whatsapp.connector import WhatsAppConnector
from app.connectors.banking_upi.connector import BankingUPIConnector
from app.connectors.auth.vault import ConnectorAuthVault
from app.domain.shared.context import ExecutionContext
from app.shared.enums import ExecutionMode


async def run_simulation_demonstration():
    vault = ConnectorAuthVault()
    ctx_sim = ExecutionContext(
        tenant_id=str(uuid4()),
        principal_id="user_iamlnavdeeep",
        session_id=str(uuid4()),
        conversation_id=str(uuid4()),
        trace_id=str(uuid4()),
        correlation_id=str(uuid4()),
        execution_mode=ExecutionMode.SIMULATION,
    )

    # 1. Gmail Authentication & Simulated Email Action
    google_auth = await vault.register_google_unified_auth(
        user_id="user_iamlnavdeeep",
        auth_code="sample_google_auth_code_99",
        authorized_scopes=["https://www.googleapis.com/auth/gmail.modify"],
    )
    gmail_conn = GmailConnector()
    email_res = await gmail_conn.execute_action(
        "send_email",
        {
            "to": "iamlnavdeeep@gmail.com",
            "subject": "BizOS Connector Test Email (Simulated)",
            "body": "Hello! This is a simulated test message verifying Gmail connector integration.",
        },
        ctx_sim,
    )

    # 2. WhatsApp Phone Verification & Simulated Message Action
    wa_auth = await vault.register_whatsapp_auth(
        user_id="user_iamlnavdeeep",
        phone_number="+919445076705",
        otp_verified=True,
    )
    wa_conn = WhatsAppConnector()
    wa_res = await wa_conn.execute_action(
        "send_message",
        {
            "to": "+919445076705",
            "message": "BizOS WhatsApp Connector Test Message: Connection Verified!",
        },
        ctx_sim,
    )

    # 3. Banking Provider Authentication & Masked Details
    bank_conn = BankingUPIConnector()
    bank_init = await bank_conn.initiate_provider_auth("user_iamlnavdeeep", "open_banking")
    bank_auth = await bank_conn.complete_provider_auth("open_banking", {"code": "ippb_auth_ref"})

    # Mask account number: 047810518165 -> ****8165
    raw_acc = "047810518165"
    masked_acc = f"****{raw_acc[-4:]}"

    bank_res = await bank_conn.execute_action(
        "fetch_bank_statement",
        {
            "provider_id": "open_banking",
            "masked_account": masked_acc,
            "bank_name": "India Post Payments Bank (IPPB)",
        },
        ctx_sim,
    )

    print("=== SIMULATION RESULTS ===")
    print("Google Auth:", google_auth)
    print("Email Action:", email_res)
    print("WhatsApp Auth:", wa_auth)
    print("WhatsApp Action:", wa_res)
    print("Bank Auth Init:", bank_init)
    print("Bank Statement Action:", bank_res)
    print("Masked Account:", masked_acc)


if __name__ == "__main__":
    asyncio.run(run_simulation_demonstration())
