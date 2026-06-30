from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RuntimeSettings(BaseSettings):
    """
    Centralized defaults and constraints for the Execution Kernel.
    """
    default_max_tokens: int = Field(default=128000, description="Default max tokens per session")
    default_max_time_ms: int = Field(default=300000, description="Default max time in ms (5 mins)")
    default_max_recursion: int = Field(default=5, description="Default max recursion depth for agents")
    default_max_retries: int = Field(default=3, description="Default max tool or task retries")
    default_max_cost_cents: int = Field(default=100, description="Default budget cap in cents")

    model_config = SettingsConfigDict(env_prefix="RUNTIME_")

runtime_settings = RuntimeSettings()
