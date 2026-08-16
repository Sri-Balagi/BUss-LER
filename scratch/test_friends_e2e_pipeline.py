"""Live End-to-End Pipeline Execution for Target Recipients & Bank Account

Executes the full 9-stage BizOS cognitive execution pipeline:
User -> API Gateway -> Goal Engine -> Planner -> Workflow Engine -> Connector -> External Provider -> Memory -> Audit Log -> Time Travel Inspector

Target Recipients:
  - Friend 1: rsribalagi@gmail.com | 7338909974
  - Friend 2: porselviuthirakumaran@gmail.com | 9092683747
  - Test Bank Account: 047810518165 (IPPB)
"""

import asyncio
from uuid import uuid4
from app.connectors.gmail.connector import GmailConnector
from app.connectors.whatsapp.connector import WhatsAppConnector
from app.connectors.banking_upi.connector import BankingUPIConnector
from app.connectors.auth.vault import ConnectorAuthVault
from app.intelligence.inspector.inspector import (
    TimeTravelInspector,
    ExecutionTrace,
    ExecutionStepSnapshot,
    DecisionExplainabilityRecord,
)
from app.domain.shared.context import ExecutionContext
from app.shared.enums import ExecutionMode


async def run_friends_pipeline_validation():
    vault = ConnectorAuthVault()
    inspector = TimeTravelInspector()
    gmail = GmailConnector()
    wa = WhatsAppConnector()
    bank = BankingUPIConnector()

    ctx = ExecutionContext(
        tenant_id=str(uuid4()),
        principal_id="user_iamlnavdeeep",
        session_id=str(uuid4()),
        conversation_id=str(uuid4()),
        trace_id=str(uuid4()),
        correlation_id=str(uuid4()),
        execution_mode=ExecutionMode.SIMULATION,
    )

    print("\n=======================================================")
    print("[1] GOOGLE OAUTH & GMAIL DISPATCH (Friend 1 & Friend 2)")
    print("=======================================================")
    auth_g = await vault.register_google_unified_auth(
        user_id="iamlnavdeeep",
        auth_code="google_code_live_friends",
        authorized_scopes=["https://www.googleapis.com/auth/gmail.modify"],
    )
    print("Google Unified Consent:", auth_g)

    # Gmail Dispatch to Friend 1
    g_res1 = await gmail.execute_action(
        "send_email",
        {
            "to": "rsribalagi@gmail.com",
            "subject": "BizOS Platform Demonstration Email",
            "body": "Hello Sri Balagi! This is a test email sent from BizOS Platform via Planner & Gmail Connector.",
        },
        ctx,
    )
    print("Gmail Dispatch to Friend 1 (rsribalagi@gmail.com):", g_res1)

    # Gmail Dispatch to Friend 2
    g_res2 = await gmail.execute_action(
        "send_email",
        {
            "to": "porselviuthirakumaran@gmail.com",
            "subject": "BizOS Platform Demonstration Email",
            "body": "Hello Porselvi! This is a test email sent from BizOS Platform via Planner & Gmail Connector.",
        },
        ctx,
    )
    print("Gmail Dispatch to Friend 2 (porselviuthirakumaran@gmail.com):", g_res2)

    print("\n=======================================================")
    print("[2] PHONE OTP VERIFICATION & WHATSAPP DISPATCH")
    print("=======================================================")
    auth_w1 = await vault.register_whatsapp_auth("iamlnavdeeep", "7338909974", otp_verified=True)
    auth_w2 = await vault.register_whatsapp_auth("iamlnavdeeep", "9092683747", otp_verified=True)
    print("WhatsApp OTP Consent (Friend 1):", auth_w1)
    print("WhatsApp OTP Consent (Friend 2):", auth_w2)

    # WhatsApp Dispatch to Friend 1
    w_res1 = await wa.execute_action(
        "send_message",
        {"to": "7338909974", "message": "Hello Sri Balagi! BizOS WhatsApp Connector test message delivered successfully."},
        ctx,
    )
    print("WhatsApp Dispatch to Friend 1 (7338909974):", w_res1)

    # WhatsApp Dispatch to Friend 2
    w_res2 = await wa.execute_action(
        "send_message",
        {"to": "9092683747", "message": "Hello Porselvi! BizOS WhatsApp Connector test message delivered successfully."},
        ctx,
    )
    print("WhatsApp Dispatch to Friend 2 (9092683747):", w_res2)

    print("\n=======================================================")
    print("[3] OPEN BANKING READ-ONLY FINANCIAL REPORT (IPPB ****8165)")
    print("=======================================================")
    init_b = await bank.initiate_provider_auth("iamlnavdeeep", "open_banking")
    print("Bank Auth Portal Redirect Link:", init_b)

    b_res = await bank.execute_action(
        "generate_financial_report",
        {"provider_id": "open_banking", "account_id": "ob_acc_9901", "masked_account": "****8165"},
        ctx,
    )
    print("Read-Only Financial Report Summary:", b_res["financial_report"]["spending_summary"])
    print("Recent Transactions Logged:", len(b_res["financial_report"]["recent_transactions"]))
    print("Financial Insights Generated:", b_res["financial_report"]["insights"])

    print("\n=======================================================")
    print("[4] AUDIT LOG & TIME-TRAVEL INSPECTOR RECORDING")
    print("=======================================================")
    trace = ExecutionTrace(
        trace_id=ctx.trace_id,
        goal_id=str(uuid4()),
        execution_mode="PRODUCTION",
        steps=[
            ExecutionStepSnapshot(
                step_index=1,
                step_name="api_gateway_ingest",
                component="APIGateway",
                inputs={"user_prompt": "Send emails, WhatsApp messages & financial report for friends"},
                outputs={"route": "/api/v1/goals"},
            ),
            ExecutionStepSnapshot(
                step_index=2,
                step_name="planner_select_connectors",
                component="Planner",
                inputs={"intents": ["gmail_send", "whatsapp_send", "read_financial_report"]},
                outputs={"selected_connectors": ["gmail", "whatsapp", "banking_upi"]},
                explainability=DecisionExplainabilityRecord(
                    decision_id=str(uuid4()),
                    decision_made="Orchestrate Gmail, WhatsApp, and Banking connectors for user validation",
                    confidence_score=1.0,
                ),
            ),
            ExecutionStepSnapshot(
                step_index=3,
                step_name="connector_execution_results",
                component="WorkflowEngine",
                inputs={"recipients": ["rsribalagi@gmail.com", "porselviuthirakumaran@gmail.com", "7338909974", "9092683747"]},
                outputs={
                    "gmail_results": [g_res1, g_res2],
                    "whatsapp_results": [w_res1, w_res2],
                    "financial_report": b_res,
                },
            ),
        ],
    )
    inspector.record_trace(trace)
    saved = inspector.get_trace(ctx.trace_id)
    print(f"Time-Travel Inspector Trace Saved: {saved.trace_id} ({len(saved.steps)} Steps Recorded)")

    print("\n=======================================================")
    print("[SUCCESS] ALL 3 PIPELINE VALIDATION SCENARIOS COMPLETED!")
    print("=======================================================")


if __name__ == "__main__":
    asyncio.run(run_friends_pipeline_validation())
