import os
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
import structlog
from app.connectors.oauth.manager import OAuthProviderManager
from app.connectors.oauth.providers.slack import SlackOAuthProvider
from app.connectors.oauth.providers.microsoft import MicrosoftOAuthProvider
from app.connectors.oauth.providers.google import GoogleOAuthProvider
from app.connectors.oauth.providers.hubspot import HubSpotOAuthProvider
from app.connectors.oauth.providers.salesforce import SalesforceOAuthProvider

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/connectors/oauth", tags=["OAuth Connectors"])

# Initialize manager and register providers
oauth_manager = OAuthProviderManager()
oauth_manager.register(SlackOAuthProvider())
oauth_manager.register(MicrosoftOAuthProvider())
oauth_manager.register(GoogleOAuthProvider())
oauth_manager.register(HubSpotOAuthProvider())
oauth_manager.register(SalesforceOAuthProvider())

@router.get("/callback")
async def oauth_callback(request: Request):
    """
    Unified OAuth callback handler for all providers.
    Expected query parameters:
    - provider: str (e.g. "slack")
    - code: str
    - state: str (used for CSRF and passing tenant/connector info)
    - error: str (if user denied access)
    """
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    error = request.query_params.get("error")

    if error:
        return HTMLResponse(f"<h2>Authorization Failed</h2><p>Error: {error}</p>", status_code=400)
    
    # Extract tenant_id and provider_id from state (e.g., default_tenant|slack)
    tenant_id = "default_tenant"
    provider_id = request.query_params.get("provider")  # Fallback if provided directly
    
    if state and "|" in state:
        parts = state.split("|")
        if len(parts) >= 2:
            tenant_id = parts[0]
            provider_id = parts[1]
            
    if not provider_id or not code:
        raise HTTPException(status_code=400, detail="Missing provider or code parameter")
        
    connector_id = provider_id

    # Fetch credentials from environment
    client_id = os.getenv(f"{provider_id.upper()}_OAUTH_CLIENT_ID")
    client_secret = os.getenv(f"{provider_id.upper()}_OAUTH_CLIENT_SECRET")
    redirect_uri = os.getenv(f"{provider_id.upper()}_OAUTH_REDIRECT_URI", "http://localhost:8080/callback")

    if not client_id or not client_secret:
        return HTMLResponse(
            f"<h2>Configuration Error</h2><p>Missing Client ID or Secret for {provider_id}.</p>", 
            status_code=500
        )

    try:
        record = await oauth_manager.exchange_and_persist(
            provider_id=provider_id,
            connector_id=connector_id,
            code=code,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            tenant_id=tenant_id
        )
        
        return HTMLResponse(f"""
        <html>
            <head><style>body {{ font-family: sans-serif; text-align: center; padding: 50px; }}</style></head>
            <body>
                <h1 style="color: #4CAF50;">Authentication Successful!</h1>
                <p>You have successfully connected <b>{provider_id.capitalize()}</b>.</p>
                <p>You can close this window and return to the terminal.</p>
            </body>
        </html>
        """)
    except Exception as exc:
        logger.error("OAuth exchange failed", error=str(exc))
        return HTMLResponse(f"<h2>Exchange Failed</h2><p>{str(exc)}</p>", status_code=500)
