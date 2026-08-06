from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    scopes: List[str] = []
    metadata: Dict[str, Any] = {}

class BaseOAuthProvider(ABC):
    """Abstract base class for all OAuth providers."""
    
    provider_id: str
    display_name: str
    auth_url_template: str
    token_endpoint: str
    revoke_endpoint: Optional[str] = None
    required_scopes: List[str] = []

    @abstractmethod
    def build_auth_url(self, client_id: str, redirect_uri: str, state: str, **kwargs) -> str:
        """Builds the authorization URL for user consent."""
        pass

    @abstractmethod
    async def exchange_code(self, code: str, client_id: str, client_secret: str, redirect_uri: str) -> TokenResponse:
        """Exchanges an authorization code for an access token."""
        pass

    @abstractmethod
    async def refresh_token(self, refresh_token: str, client_id: str, client_secret: str) -> TokenResponse:
        """Refreshes an expired access token."""
        pass

    async def revoke_token(self, token: str, client_id: str = "", client_secret: str = "") -> None:
        """Revokes a token (access or refresh) if the provider supports it."""
        pass
