from pydantic import BaseModel, Field
from typing import Optional, List

class CapabilityManifest(BaseModel):
    """
    Deployment-only information for a capability.
    """
    version: str = Field(..., description="Semantic version of the capability.")
    author: str = Field(..., description="Author or organization.")
    package: str = Field(..., description="Package identifier.")
    dependencies: List[str] = Field(default_factory=list, description="List of dependency packages.")
    plugin_source: Optional[str] = Field(default=None, description="URL or path to plugin source.")
    checksum: Optional[str] = Field(default=None, description="Checksum for verification.")
