"""Delta Sync State Store

A lightweight key-value store for persisting Graph API delta links.
In production, this could be backed by Supabase or another KV store.
For now, we simulate persistence via a simple interface.
"""

import structlog
from typing import Optional, Dict

logger = structlog.get_logger(__name__)

class DeltaStateStore:
    """Mock store for delta links."""
    
    _store: Dict[str, str] = {}
    
    @classmethod
    def _key(cls, connector_id: str, resource: str, tenant_id: str) -> str:
        return f"{tenant_id}:{connector_id}:{resource}"
        
    @classmethod
    def get_delta_link(cls, connector_id: str, resource: str, tenant_id: str) -> Optional[str]:
        """Fetch the persisted delta link for the given resource."""
        key = cls._key(connector_id, resource, tenant_id)
        link = cls._store.get(key)
        logger.debug("Fetched delta link", key=key, found=link is not None)
        return link
        
    @classmethod
    def set_delta_link(cls, connector_id: str, resource: str, tenant_id: str, link: str) -> None:
        """Persist a new delta link for the given resource."""
        key = cls._key(connector_id, resource, tenant_id)
        cls._store[key] = link
        logger.debug("Saved delta link", key=key)
        
    @classmethod
    def clear_delta_link(cls, connector_id: str, resource: str, tenant_id: str) -> None:
        """Clear the delta link (e.g. on full resync or token expiration)."""
        key = cls._key(connector_id, resource, tenant_id)
        if key in cls._store:
            del cls._store[key]
            logger.debug("Cleared delta link", key=key)
