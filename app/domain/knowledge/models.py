import enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field

from app.domain.common.biz_object import BizObject


class EntityType(str, enum.Enum):
    EMPLOYEE = "Employee"
    DEPARTMENT = "Department"
    ORGANIZATION = "Organization"
    CUSTOMER = "Customer"
    PRODUCT = "Product"
    PROJECT = "Project"
    VENDOR = "Vendor"
    ASSET = "Asset"
    DOCUMENT = "Document"
    WORKFLOW = "Workflow"


class RelationshipType(str, enum.Enum):
    REPORTS_TO = "REPORTS_TO"
    BELONGS_TO = "BELONGS_TO"
    MANAGES = "MANAGES"
    OWNS = "OWNS"
    WORKS_ON = "WORKS_ON"
    PURCHASED = "PURCHASED"
    DEPENDS_ON = "DEPENDS_ON"
    RELATED_TO = "RELATED_TO"
    PART_OF = "PART_OF"


class KnowledgeNode(BizObject):
    """Base class for all business knowledge graph nodes."""
    entity_type: EntityType = Field(..., description="The type of this entity in the ontology.")
    name: str = Field(..., description="Human readable name of the entity.")
    description: Optional[str] = Field(default=None, description="Detailed description.")
    
    # Future-proofing for Intelligence Layers
    version: int = Field(default=1, description="Version for optimistic concurrency and tracking.")
    provenance: Optional[str] = Field(default=None, description="Source of this knowledge (e.g., 'System', 'User:XYZ', 'Agent:ABC').")
    embedding_refs: List[str] = Field(default_factory=list, description="References to semantic vector storage IDs.")
    
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Flexible metadata extension properties.")


class KnowledgeEdge(BizObject):
    """Represents a directional relationship between two nodes in the graph."""
    source_id: UUID = Field(..., description="ID of the origin node.")
    target_id: UUID = Field(..., description="ID of the destination node.")
    relationship_type: RelationshipType = Field(..., description="The type of relationship.")
    
    # Future-proofing for Intelligence Layers
    version: int = Field(default=1, description="Version for optimistic concurrency and tracking.")
    provenance: Optional[str] = Field(default=None, description="Source of this knowledge.")
    
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Properties of the edge (e.g. weight, since_date).")


# Strongly Typed Business Entities

class Employee(KnowledgeNode):
    entity_type: EntityType = Field(default=EntityType.EMPLOYEE, frozen=True)
    title: Optional[str] = None
    email: Optional[str] = None
    department_id: Optional[UUID] = None

class Department(KnowledgeNode):
    entity_type: EntityType = Field(default=EntityType.DEPARTMENT, frozen=True)
    manager_id: Optional[UUID] = None

class Organization(KnowledgeNode):
    entity_type: EntityType = Field(default=EntityType.ORGANIZATION, frozen=True)
    industry: Optional[str] = None

class Customer(KnowledgeNode):
    entity_type: EntityType = Field(default=EntityType.CUSTOMER, frozen=True)
    account_manager_id: Optional[UUID] = None

class Product(KnowledgeNode):
    entity_type: EntityType = Field(default=EntityType.PRODUCT, frozen=True)
    price: Optional[float] = None
    category: Optional[str] = None

class Project(KnowledgeNode):
    entity_type: EntityType = Field(default=EntityType.PROJECT, frozen=True)
    status: str = Field(default="PLANNED")

class Vendor(KnowledgeNode):
    entity_type: EntityType = Field(default=EntityType.VENDOR, frozen=True)
    contact_email: Optional[str] = None

class Asset(KnowledgeNode):
    entity_type: EntityType = Field(default=EntityType.ASSET, frozen=True)
    asset_type: str = Field(default="SOFTWARE")

class Document(KnowledgeNode):
    entity_type: EntityType = Field(default=EntityType.DOCUMENT, frozen=True)
    uri: Optional[str] = None

class WorkflowEntity(KnowledgeNode):
    entity_type: EntityType = Field(default=EntityType.WORKFLOW, frozen=True)
    status: str = Field(default="IDLE")
