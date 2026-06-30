from pydantic import BaseModel, Field


class AgentManifest(BaseModel):
    """
    Contains purely external deployment and packaging metadata.
    Ignored by the execution and routing mechanics.
    """
    version: str = Field(description="Semantic version of the agent (e.g., '1.0.0')")
    deployment_source: str = Field(description="Source of deployment (e.g., 'builtin', 'plugin-v1.2')")
    author: str = Field(default="BizOS", description="Author or organization that created the agent")
    dependencies: list[str] = Field(default_factory=list, description="List of external dependencies or plugins required")
