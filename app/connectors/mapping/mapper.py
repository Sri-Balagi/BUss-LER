"""Data Mapping Framework models and mapper interface."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Any
from pydantic import BaseModel, Field
from app.connectors.canonical.base import CanonicalObject

VendorT = TypeVar("VendorT")
CanonicalT = TypeVar("CanonicalT", bound=CanonicalObject)


class FieldMap(BaseModel):
    source_field: str
    target_field: str
    transform_func: str | None = None  # e.g., "to_datetime", "to_lower"
    default_value: Any = None


class MappingRule(BaseModel):
    rule_id: str
    vendor_type: str
    canonical_type: str
    field_maps: list[FieldMap] = Field(default_factory=list)


class MappingResult(BaseModel, Generic[CanonicalT]):
    success: bool
    canonical_object: CanonicalT | None = None
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class IDataMapper(ABC, Generic[VendorT, CanonicalT]):
    """Abstract interface for mapping vendor objects to canonical models."""

    @abstractmethod
    def map(self, vendor_object: VendorT, connector_id: str, profile_id: str = "default") -> CanonicalT:
        """Transform raw vendor data into a canonical BizOS model."""

    @abstractmethod
    def reverse_map(self, canonical_object: CanonicalT) -> VendorT:
        """Transform a canonical model back into a vendor-specific object."""
