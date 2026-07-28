import logging
from datetime import datetime, timezone

logger = logging.getLogger("bizos.audit")

class AuditLogger:
    def log(self, action: str, resource: str, actor: str, outcome: str, details: dict | None = None):
        """Log an audit event."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actor": actor,
            "action": action,
            "resource": resource,
            "outcome": outcome,
            "details": details or {}
        }
        logger.info(f"AUDIT: {entry}")
