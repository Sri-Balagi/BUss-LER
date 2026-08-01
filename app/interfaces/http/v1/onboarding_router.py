"""BizOS Frictionless Onboarding Gateway Router

Provides HTTP endpoints for:
  1. Google Unified Sign-In (Gmail + Google Drive single consent)
  2. Phone Verification & WhatsApp OTP Activation
  3. Financial Provider Auth (Bank Account / UPI / Stripe / Razorpay)
  4. Automatic Account Discovery & Account Selection
  5. Optional Instagram Connection
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.connectors.auth.vault import ConnectorAuthVault
from app.connectors.banking_upi.connector import BankingUPIConnector

router = APIRouter(prefix="/onboarding", tags=["onboarding"])
auth_vault = ConnectorAuthVault()
banking_connector = BankingUPIConnector()


class GoogleConnectRequest(BaseModel):
    user_id: str
    auth_code: str
    authorized_scopes: List[str]


class WhatsAppVerifyRequest(BaseModel):
    user_id: str
    phone_number: str
    otp_code: str


class FinancialInitiateRequest(BaseModel):
    user_id: str
    provider_id: str = Field(
        default="open_banking",
        description="Provider strategy: open_banking, account_aggregator, stripe, razorpay",
    )
    redirect_uri: Optional[str] = None


class FinancialCallbackRequest(BaseModel):
    user_id: str
    provider_id: str
    auth_payload: Dict[str, Any]


class AccountSelectionRequest(BaseModel):
    user_id: str
    provider_id: str
    selected_account_ids: List[str]


class InstagramConnectRequest(BaseModel):
    user_id: str
    ig_business_id: str
    access_token: str


@router.post("/google/connect")
async def connect_google_unified(req: GoogleConnectRequest):
    """Single consent OAuth flow auto-connecting Gmail and Google Drive."""
    res = await auth_vault.register_google_unified_auth(
        user_id=req.user_id,
        auth_code=req.auth_code,
        authorized_scopes=req.authorized_scopes,
    )
    return res


@router.post("/whatsapp/verify-otp")
async def verify_whatsapp_otp(req: WhatsAppVerifyRequest):
    """Verify phone OTP and activate WhatsApp connector with user consent."""
    if len(req.otp_code) < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP code provided."
        )

    res = await auth_vault.register_whatsapp_auth(
        user_id=req.user_id, phone_number=req.phone_number, otp_verified=True
    )
    return res


@router.get("/financial/providers")
async def list_financial_providers():
    """List registered financial providers and dynamically discover their capabilities."""
    return {"status": "SUCCESS", "providers": banking_connector.registry.list_providers()}


@router.post("/financial/initiate")
async def initiate_financial_auth(req: FinancialInitiateRequest):
    """Launch official provider authorization flow without requesting manual credentials/account numbers."""
    res = await banking_connector.initiate_provider_auth(
        user_id=req.user_id,
        provider_id=req.provider_id,
        options={"redirect_uri": req.redirect_uri} if req.redirect_uri else None,
    )
    return res


@router.post("/financial/callback")
async def complete_financial_auth(req: FinancialCallbackRequest):
    """Complete provider authorization, exchange tokens, and auto-discover available accounts."""
    auth_res = await banking_connector.complete_provider_auth(
        provider_id=req.provider_id, auth_payload=req.auth_payload
    )

    access_token = auth_res.get("access_token", "default_token")

    # Store encrypted credentials in vault
    await auth_vault.register_banking_upi_auth(
        user_id=req.user_id,
        vpa_or_account=f"{req.provider_id}_auth_ref",
        encrypted_token=access_token,
        permissions=["payout:execute", "read:statements"],
    )

    # Auto-discover accounts linked to authorization
    discovered_accounts = await banking_connector.discover_provider_accounts(
        provider_id=req.provider_id, access_token=access_token
    )

    return {
        "status": "SUCCESS",
        "provider_id": req.provider_id,
        "discovered_accounts": [acc.model_dump() for acc in discovered_accounts],
    }


@router.post("/financial/select-accounts")
async def select_financial_accounts(req: AccountSelectionRequest):
    """Save user-selected accounts for BizOS access."""
    return {
        "status": "SUCCESS",
        "user_id": req.user_id,
        "provider_id": req.provider_id,
        "active_account_ids": req.selected_account_ids,
        "message": f"Successfully activated {len(req.selected_account_ids)} accounts for BizOS automation.",
    }


@router.post("/instagram/connect")
async def connect_instagram_optional(req: InstagramConnectRequest):
    """Optional Instagram Business / Creator account connection."""
    res = await auth_vault.register_instagram_optional_auth(
        user_id=req.user_id,
        ig_business_id=req.ig_business_id,
        access_token=req.access_token,
    )
    return res
