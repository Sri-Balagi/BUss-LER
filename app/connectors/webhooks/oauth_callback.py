import os
import httpx
import smtplib
from email.mime.text import MIMEText
from pydantic import BaseModel
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
import structlog
from app.connectors.oauth.manager import OAuthProviderManager
from app.connectors.oauth.providers.slack import SlackOAuthProvider
from app.connectors.oauth.providers.microsoft import MicrosoftOAuthProvider
from app.connectors.oauth.providers.google import GoogleOAuthProvider
from app.connectors.oauth.providers.hubspot import HubSpotOAuthProvider
from app.connectors.oauth.providers.salesforce import SalesforceOAuthProvider

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="", tags=["OAuth & Auth Connectors"])

# Initialize manager and register providers
oauth_manager = OAuthProviderManager()
oauth_manager.register(SlackOAuthProvider())
oauth_manager.register(MicrosoftOAuthProvider())
oauth_manager.register(GoogleOAuthProvider())
oauth_manager.register(HubSpotOAuthProvider())
oauth_manager.register(SalesforceOAuthProvider())

class EmailVerificationPayload(BaseModel):
    email: str
    code: str

@router.post("/auth/send-verification-email")
@router.post("/connectors/auth/send-verification-email")
async def send_verification_email_endpoint(payload: EmailVerificationPayload):
    sender = os.getenv("GMAIL_SENDER", "iamlnavdeep@gmail.com")
    password = os.getenv("GMAIL_APP_PASSWORD", "qjjk jnnp jxet pqta")
    
    body = (
        f"Hello,\n\n"
        f"Your 6-digit BizOS security verification code is: {payload.code}\n\n"
        f"Enter this code to access your BizOS workspace.\n\n"
        f"Regards,\n"
        f"BizOS Security Team"
    )
    msg = MIMEText(body)
    msg['Subject'] = f"Your BizOS Verification Code: {payload.code}"
    msg['From'] = f"BizOS Security <{sender}>"
    msg['To'] = payload.email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, [payload.email], msg.as_string())
        logger.info("Real verification email sent successfully", recipient=payload.email, code=payload.code)
        return {"status": "sent", "recipient": payload.email, "message": "Verification email dispatched via Gmail SMTP."}
    except Exception as exc:
        logger.error("Failed to dispatch verification email", recipient=payload.email, error=str(exc))
        return {"status": "fallback", "recipient": payload.email, "error": str(exc)}

@router.get("/google/callback")
@router.get("/connectors/google/callback")
@router.get("/oauth/callback")
async def oauth_callback(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    error = request.query_params.get("error")

    if error:
        logger.warning("OAuth authorization error received", error=error)
        return RedirectResponse(url="http://localhost:3000/dashboard?auth_error=" + str(error))
    
    tenant_id = "default_tenant"
    provider_id = request.query_params.get("provider", "google")
    
    if state and "|" in state:
        parts = state.split("|")
        if len(parts) >= 2:
            tenant_id = parts[0]
            provider_id = parts[1]
            
    connector_id = provider_id

    client_id = os.getenv(f"{provider_id.upper()}_CLIENT_ID") or os.getenv(f"{provider_id.upper()}_OAUTH_CLIENT_ID")
    client_secret = os.getenv(f"{provider_id.upper()}_CLIENT_SECRET") or os.getenv(f"{provider_id.upper()}_OAUTH_CLIENT_SECRET")
    redirect_uri = os.getenv(f"{provider_id.upper()}_REDIRECT_URI", "http://localhost:8000/api/v1/connectors/google/callback")

    user_email = ""

    if client_id and client_secret and code:
        try:
            tokens = await oauth_manager.exchange_and_persist(
                provider_id=provider_id,
                connector_id=connector_id,
                code=code,
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                tenant_id=tenant_id
            )
            if tokens and tokens.access_token:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    res = await client.get(
                        "https://www.googleapis.com/oauth2/v2/userinfo",
                        headers={"Authorization": f"Bearer {tokens.access_token}"}
                    )
                    if res.status_code == 200:
                        user_info = res.json()
                        user_email = user_info.get("email", "")
        except Exception as exc:
            logger.error("OAuth exchange warning", error=str(exc))

    target_url = f"http://localhost:3000/auth/google/callback?email={user_email or ''}"
    if code:
        target_url += f"&code={code}"
    return RedirectResponse(url=target_url)
