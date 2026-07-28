"""Reusable Horizontal Operations & Resource Scheduling Capability Module."""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class ShiftResource(BaseModel):
    resource_id: str
    name: str
    role: str
    status: str = "AVAILABLE"  # AVAILABLE, ON_SHIFT, ON_LEAVE


class OperationsCapabilityModule:
    """Horizontal Operations & Resource Scheduling capability engine."""

    def __init__(self):
        self._resources: Dict[str, ShiftResource] = {}

    def register_resource(self, res: ShiftResource) -> None:
        self._resources[res.resource_id] = res

    def promote_or_assign(self, resource_id: str, new_role: str) -> ShiftResource:
        if resource_id not in self._resources:
            self._resources[resource_id] = ShiftResource(resource_id=resource_id, name="Staff Member", role=new_role)
        res = self._resources[resource_id]
        res.role = new_role
        res.status = "ON_SHIFT"
        return res
