from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, Any
import structlog
from .base_provider import BaseOAuthProvider
from .token_repository import OAuthTokenRepository, OAuthTokenRecord

logger = structlog.get_logger(__name__)

class OAuthProviderManager:
    """Manages OAuth providers and the lifecycle of their tokens."""
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._providers = {}
            cls._instance._token_repo = OAuthTokenRepository()
        return cls._instance

    def register(self, provider: BaseOAuthProvider) -> None:
        """Registers a new OAuth provider."""
        self._providers[provider.provider_id] = provider
        logger.info(f"Registered OAuth provider: {provider.provider_id}")

    def get_provider(self, provider_id: str) -> BaseOAuthProvider:
        provider = self._providers.get(provider_id)
        if not provider:
            raise ValueError(f"OAuth provider {provider_id} not registered")
        return provider

    def get_auth_url(self, provider_id: str, client_id: str, redirect_uri: str, state: str, **kwargs) -> str:
        provider = self.get_provider(provider_id)
        return provider.build_auth_url(client_id, redirect_uri, state, **kwargs)

    async def exchange_and_persist(
        self, provider_id: str, connector_id: str, code: str, client_id: str, client_secret: str, 
        redirect_uri: str, tenant_id: str = "default_tenant", account_id: str = "default"
    ) -> OAuthTokenRecord:
        """Exchanges a code for tokens and persists them."""
        provider = self.get_provider(provider_id)
        
        # Exchange code for tokens
        token_response = await provider.exchange_code(code, client_id, client_secret, redirect_uri)
        
        # Calculate expiration
        expires_at = None
        if token_response.expires_in:
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=token_response.expires_in)

        # Create record
        record = OAuthTokenRecord(
            tenant_id=tenant_id,
            provider_id=provider_id,
            connector_id=connector_id,
            account_id=account_id,
            access_token=token_response.access_token,
            refresh_token=token_response.refresh_token,
            scopes=token_response.scopes,
            expires_at=expires_at
        )

        # Persist to DB
        await self._token_repo.upsert(record)
        return record

    async def get_live_token(
        self, provider_id: str, tenant_id: str = "default_tenant", 
        account_id: str = "default", client_id: str = "", client_secret: str = ""
    ) -> str:
        """Gets a valid access token, auto-refreshing if expired."""
        record = await self._token_repo.get(provider_id, tenant_id, account_id)
        if not record:
            raise ValueError(f"No tokens found for provider {provider_id} and tenant {tenant_id}")

        # Check expiration (with a 5-minute buffer)
        if record.expires_at and record.expires_at < (datetime.now(timezone.utc) + timedelta(minutes=5)):
            logger.info("Token expired or expiring soon, attempting refresh", provider_id=provider_id)
            if not record.refresh_token:
                raise ValueError("Token expired and no refresh token available")
            
            provider = self.get_provider(provider_id)
            new_tokens = await provider.refresh_token(record.refresh_token, client_id, client_secret)
            
            # Update record
            record.access_token = new_tokens.access_token
            if new_tokens.refresh_token:
                record.refresh_token = new_tokens.refresh_token
            
            if new_tokens.expires_in:
                record.expires_at = datetime.now(timezone.utc) + timedelta(seconds=new_tokens.expires_in)
            
            # Persist refreshed token
            await self._token_repo.upsert(record)
            logger.info("Successfully refreshed and persisted token", provider_id=provider_id)

        return record.access_token

    async def get_live_token_record(
        self, provider_id: str, tenant_id: str = "default_tenant", 
        account_id: str = "default", client_id: str = "", client_secret: str = ""
    ) -> OAuthTokenRecord:
        """Gets a valid token record (including metadata), auto-refreshing if expired."""
        record = await self._token_repo.get(provider_id, tenant_id, account_id)
        if not record:
            raise ValueError(f"No tokens found for provider {provider_id} and tenant {tenant_id}")

        # Check expiration (with a 5-minute buffer)
        if record.expires_at and record.expires_at < (datetime.now(timezone.utc) + timedelta(minutes=5)):
            logger.info("Token expired or expiring soon, attempting refresh", provider_id=provider_id)
            if not record.refresh_token:
                raise ValueError("Token expired and no refresh token available")
            
            provider = self.get_provider(provider_id)
            token_response = await provider.refresh_token(record.refresh_token, client_id, client_secret)
            
            expires_at = None
            if token_response.expires_in:
                expires_at = datetime.now(timezone.utc) + timedelta(seconds=token_response.expires_in)
                
            updated_record = OAuthTokenRecord(
                id=record.id,
                tenant_id=tenant_id,
                account_id=account_id,
                provider_id=provider_id,
                connector_id=record.connector_id,
                access_token=token_response.access_token,
                refresh_token=token_response.refresh_token or record.refresh_token,
                expires_at=expires_at,
                scopes=token_response.scopes or record.scopes,
                metadata=token_response.metadata or record.metadata
            )
            
            await self._token_repo.save(updated_record)
            return updated_record
            
        return record

    async def revoke_and_delete(
        self, provider_id: str, tenant_id: str = "default_tenant", 
        account_id: str = "default", client_id: str = "", client_secret: str = ""
    ) -> None:
        """Revokes the token at the provider and deletes it from the database."""
        record = await self._token_repo.get(provider_id, tenant_id, account_id)
        if record:
            provider = self.get_provider(provider_id)
            await provider.revoke_token(record.access_token, client_id, client_secret)
            await self._token_repo.delete(provider_id, tenant_id, account_id)
            logger.info("Token revoked and deleted", provider_id=provider_id)
