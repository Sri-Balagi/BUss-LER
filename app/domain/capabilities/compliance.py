"""Reusable Horizontal Compliance & Audit Capability Module."""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class ComplianceAlert(BaseModel):
    alert_id: str
    rule_name: str
    severity: str  # CRITICAL, HIGH, MEDIUM
    details: str
    requires_human_approval: bool = True
    approved: bool = False


class ComplianceCapabilityModule:
    """Horizontal Compliance & Audit capability engine."""

    def __init__(self):
        self._alerts: List[ComplianceAlert] = []

    def flag_violation(self, rule_name: str, details: str, severity: str = "HIGH") -> ComplianceAlert:
        alert = ComplianceAlert(
            alert_id=f"ALT-{len(self._alerts)+1:03d}",
            rule_name=rule_name,
            severity=severity,
            details=details,
            requires_human_approval=severity in ("CRITICAL", "HIGH"),
        )
        self._alerts.append(alert)
        return alert

    def approve_alert(self, alert_id: str) -> bool:
        for a in self._alerts:
            if a.alert_id == alert_id:
                a.approved = True
                return True
        return False
