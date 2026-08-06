import json
import base64
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
import structlog
from app.infrastructure.persistence.postgres.supabase import SupabaseService
from app.config import get_settings

logger = structlog.get_logger(__name__)

class OAuthTokenRecord(BaseModel):
    id: Optional[str] = None
    tenant_id: str
    provider_id: str
    connector_id: str
    account_id: str = "default"
    access_token: str
    refresh_token: Optional[str] = None
    scopes: List[str] = []
    expires_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class OAuthTokenRepository:
    """PostgreSQL/Supabase repository for storing OAuth tokens."""
    
    def __init__(self):
        # We assume settings are loaded and available
        self.settings = get_settings()
        self.encryption_key = self.settings.connector_vault_encryption_key if hasattr(self.settings, 'connector_vault_encryption_key') else "default-32-byte-secret-key-12345"

    def _encrypt(self, token: str) -> str:
        if not token:
            return token
        # Basic encryption simulation for now (base64) - in production replace with AES-256
        encoded = base64.b64encode(token.encode()).decode()
        return f"enc_v2_{encoded}"

    def _decrypt(self, encrypted_token: str) -> str:
        if not encrypted_token:
            return encrypted_token
        if encrypted_token.startswith("enc_v2_"):
            raw = encrypted_token.replace("enc_v2_", "")
            return base64.b64decode(raw.encode()).decode()
        return encrypted_token

    async def upsert(self, record: OAuthTokenRecord) -> None:
        client = await SupabaseService.get_client(self.settings)
        
        data = {
            "tenant_id": record.tenant_id,
            "provider_id": record.provider_id,
            "connector_id": record.connector_id,
            "account_id": record.account_id,
            "access_token": self._encrypt(record.access_token),
            "refresh_token": self._encrypt(record.refresh_token) if record.refresh_token else None,
            "scopes": record.scopes,
            "expires_at": record.expires_at.isoformat() if record.expires_at else None,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Upsert based on unique constraint (tenant_id, provider_id, account_id)
        response = await client.table("connector_oauth_tokens").upsert(
            data, on_conflict="tenant_id, provider_id, account_id"
        ).execute()
        
        logger.info("Upserted OAuth token record", provider=record.provider_id, tenant=record.tenant_id)

    async def get(self, provider_id: str, tenant_id: str, account_id: str = "default") -> Optional[OAuthTokenRecord]:
        client = await SupabaseService.get_client(self.settings)
        
        response = await client.table("connector_oauth_tokens").select("*").eq(
            "tenant_id", tenant_id
        ).eq("provider_id", provider_id).eq("account_id", account_id).execute()
        
        if not response.data:
            return None
            
        row = response.data[0]
        
        expires_at = datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00")) if row.get("expires_at") else None
        created_at = datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")) if row.get("created_at") else None
        updated_at = datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00")) if row.get("updated_at") else None
        
        return OAuthTokenRecord(
            id=row["id"],
            tenant_id=row["tenant_id"],
            provider_id=row["provider_id"],
            connector_id=row["connector_id"],
            account_id=row["account_id"],
            access_token=self._decrypt(row["access_token"]),
            refresh_token=self._decrypt(row["refresh_token"]) if row.get("refresh_token") else None,
            scopes=row.get("scopes", []),
            expires_at=expires_at,
            created_at=created_at,
            updated_at=updated_at
        )

    async def delete(self, provider_id: str, tenant_id: str, account_id: str = "default") -> None:
        client = await SupabaseService.get_client(self.settings)
        await client.table("connector_oauth_tokens").delete().eq(
            "tenant_id", tenant_id
        ).eq("provider_id", provider_id).eq("account_id", account_id).execute()
        logger.info("Deleted OAuth token record", provider=provider_id, tenant=tenant_id)
