"""Entity domain models for Milestone 1.

Extends the base Entity models defined in app.models.schemas with
update-specific schemas needed for the Digital Twin System API.

The base Entity and EntityCreate models remain in app.models.schemas
(Milestone 0). This module adds only M1-specific schemas.
"""

from pydantic import Field

from app.models.enums import EntityType
from app.models.schemas import DomainBaseModel


class EntityUpdate(DomainBaseModel):
    """Request schema for updating an entity.

    All fields are optional. Only provided (non-None) fields
    will be applied to the existing entity record.
    """

    name: str | None = Field(
        None,
        min_length=1,
        max_length=200,
        description="Display name for the entity.",
    )
    entity_type: EntityType | None = Field(
        None,
        description="Updated entity type.",
    )
    description: str | None = Field(
        None,
        max_length=2000,
        description="Updated description.",
    )
    metadata: dict | None = Field(
        None,
        description="Updated metadata. Replaces entire metadata object.",
    )
