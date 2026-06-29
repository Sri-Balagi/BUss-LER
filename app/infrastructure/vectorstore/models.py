from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import Field

from app.shared.enums import MemoryCategory, MemorySource
from app.interfaces.http.schemas.base import DomainBaseModel


class MemoryVectorPayload(DomainBaseModel):
    """The metadata payload stored alongside the vector in Qdrant.

    This schema is minimal by design. It only contains the fields required
    for vector filtering, hybrid retrieval, and recency ranking.
    Full memory data remains in PostgreSQL.
    """

    memory_id: UUID = Field(
        ..., description="The unique identifier matching the PostgreSQL memory record."
    )
    twin_id: UUID = Field(..., description="The Digital Twin this memory belongs to.")
    memory_category: MemoryCategory = Field(
        ..., description="The business classification of the memory."
    )
    source: MemorySource = Field(..., description="The source system or interaction.")
    importance: Decimal = Field(
        ..., max_digits=3, decimal_places=2, description="Significance score."
    )
    created_at: datetime = Field(
        ..., description="Timestamp of memory creation for time-weighted retrieval."
    )
    updated_at: datetime = Field(..., description="Timestamp of last modification.")


class MemoryVectorPoint(DomainBaseModel):
    """Represents a fully resolved Qdrant Point for ingestion or retrieval."""

    id: UUID = Field(
        ..., description="The Qdrant Point ID, which matches the memory_id."
    )
    vector: list[float] = Field(..., description="The raw embedding vector.")
    payload: MemoryVectorPayload = Field(
        ..., description="The structured metadata payload."
    )
    score: Optional[float] = Field(
        None, description="Similarity score returned during search."
    )
