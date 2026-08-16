from pydantic import BaseModel, Field


class CapabilityManifest(BaseModel):
    """
    Deployment-only information for a capability.
    """

    version: str = Field(..., description="Semantic version of the capability.")
    author: str = Field(..., description="Author or organization.")
    package: str = Field(..., description="Package identifier.")
    dependencies: list[str] = Field(
        default_factory=list, description="List of dependency packages."
    )
    plugin_source: str | None = Field(default=None, description="URL or path to plugin source.")
    checksum: str | None = Field(default=None, description="Checksum for verification.")
