
from pydantic import BaseModel, Field


class AppManifest(BaseModel):
    """
    Standard schema for declaring a BizOS Application or Plugin.
    Validated by the BizOS Registry and CLI Scaffolder.
    """
    name: str = Field(..., description="Unique application identifier.")
    version: str = Field(default="0.1.0", description="SemVer version string.")
    description: str = Field(default="", description="Human-readable description.")
    author: str = Field(default="unknown")

    # Dependencies required by this app
    dependencies: list[str] = Field(default_factory=list)

    # Required permissions (e.g., 'fs:read', 'network:external')
    permissions: list[str] = Field(default_factory=list)

    # Entry points
    entrypoint: str | None = None
