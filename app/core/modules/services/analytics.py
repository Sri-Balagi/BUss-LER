"""Reporting & Analytics Framework for registering module KPIs and metrics."""

from pydantic import BaseModel


class ModuleKPISpec(BaseModel):
    """Specification for a Business KPI exposed by a module."""

    kpi_id: str
    module_id: str
    name: str
    description: str
    unit: str = ""
    target_value: float | None = None


class ModuleAnalyticsRegistry:
    """Registry aggregating KPIs and analytics descriptors from modules."""

    def __init__(self) -> None:
        self._kpis: dict[str, ModuleKPISpec] = {}

    def register_kpi(self, kpi: ModuleKPISpec) -> None:
        """Register a new KPI descriptor."""
        self._kpis[kpi.kpi_id] = kpi

    def list_kpis_for_module(self, module_id: str) -> list[ModuleKPISpec]:
        """Fetch all KPIs for a given module."""
        return [k for k in self._kpis.values() if k.module_id == module_id]
