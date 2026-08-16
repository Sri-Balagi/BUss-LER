"""Live HTTP API Onboarding Flow Test

Executes the real FastAPI Onboarding Endpoints (/api/v1/onboarding/*)
to simulate how a frontend web app / mobile app interacts with BizOS.
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.interfaces.http.v1.onboarding_router import router as onboarding_router

# Build FastAPI app with onboarding router
app = FastAPI(title="BizOS Onboarding Gateway Test")
app.include_router(onboarding_router, prefix="/api/v1")

client = TestClient(app)


def test_full_onboarding_http_flow():
    print("\n=======================================================")
    print("[STEP 1] Discover Financial Providers & Capabilities")
    print("=======================================================")
    res1 = client.get("/api/v1/onboarding/financial/providers")
    print("GET /financial/providers:", res1.json())
    assert res1.status_code == 200

    print("\n=======================================================")
    print("[STEP 2] Google Unified Sign-In (Gmail + Drive)")
    print("=======================================================")
    payload_google = {
        "user_id": "iamlnavdeeep",
        "auth_code": "google_oauth_code_xyz123",
        "authorized_scopes": [
            "https://www.googleapis.com/auth/gmail.modify",
            "https://www.googleapis.com/auth/drive.file",
        ],
    }
    res2 = client.post("/api/v1/onboarding/google/connect", json=payload_google)
    print("POST /google/connect:", res2.json())
    assert res2.status_code == 200

    print("\n=======================================================")
    print("[STEP 3] Phone Verification & WhatsApp Activation")
    print("=======================================================")
    payload_wa = {
        "user_id": "iamlnavdeeep",
        "phone_number": "9445076705",
        "otp_code": "889900",
    }
    res3 = client.post("/api/v1/onboarding/whatsapp/verify-otp", json=payload_wa)
    print("POST /whatsapp/verify-otp:", res3.json())
    assert res3.status_code == 200

    print("\n=======================================================")
    print("[STEP 4] Financial Provider Auth & Account Discovery")
    print("=======================================================")
    payload_fin_init = {
        "user_id": "iamlnavdeeep",
        "provider_id": "open_banking",
        "redirect_uri": "https://app.bizos.ai/callback",
    }
    res4 = client.post("/api/v1/onboarding/financial/initiate", json=payload_fin_init)
    print("POST /financial/initiate:", res4.json())
    assert res4.status_code == 200

    payload_fin_cb = {
        "user_id": "iamlnavdeeep",
        "provider_id": "open_banking",
        "auth_payload": {"code": "ippb_auth_ref_047810518165"},
    }
    res5 = client.post("/api/v1/onboarding/financial/callback", json=payload_fin_cb)
    discovered = res5.json()
    print("POST /financial/callback (Discovered Accounts):", discovered)
    assert res5.status_code == 200

    acc_id = discovered["discovered_accounts"][0]["account_id"]

    print("\n=======================================================")
    print("[STEP 5] Account Selection for Automation")
    print("=======================================================")
    payload_select = {
        "user_id": "iamlnavdeeep",
        "provider_id": "open_banking",
        "selected_account_ids": [acc_id],
    }
    res6 = client.post("/api/v1/onboarding/financial/select-accounts", json=payload_select)
    print("POST /financial/select-accounts:", res6.json())
    assert res6.status_code == 200

    print("\n=======================================================")
    print("[STEP 6] Optional Instagram Connection")
    print("=======================================================")
    payload_ig = {
        "user_id": "iamlnavdeeep",
        "ig_business_id": "ig_biz_17841400",
        "access_token": "ig_oauth_tok_sample",
    }
    res7 = client.post("/api/v1/onboarding/instagram/connect", json=payload_ig)
    print("POST /instagram/connect:", res7.json())
    assert res7.status_code == 200

    print("\n=======================================================")
    print("[SUCCESS] FULL HTTP ONBOARDING FLOW EXECUTED CLEANLY!")
    print("=======================================================")


if __name__ == "__main__":
    test_full_onboarding_http_flow()
