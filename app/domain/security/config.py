from pydantic import BaseModel, Field, field_validator
import base64

class SecurityConfig(BaseModel):
    """
    Centralized cryptographic configuration for the security module.
    Instances of this config are passed to infrastructure implementations
    so they do not read environment variables directly.
    """
    encryption_key: bytes = Field(..., description="The decoded AES-256-GCM key (32 bytes)")
    bcrypt_rounds: int = Field(12, ge=4, description="Number of rounds for bcrypt hashing")
    token_length_bytes: int = Field(32, ge=16, description="Byte length for generated tokens")
    jwt_keys: dict[str, str] = Field(default_factory=dict, description="Dictionary of Key IDs (kid) to their signing keys/secrets")
    
    @classmethod
    def from_settings(cls, key_base64: str | None, rounds: int = 12, jwt_secret: str | None = None) -> "SecurityConfig":
        """Builds the config, applying fail-fast validation for the encryption key."""
        if not key_base64:
            # We already validate in Settings that prod has a key, so if missing here, it's dev fallback
            key = b'0' * 32
        else:
            try:
                key = base64.b64decode(key_base64)
            except Exception as e:
                raise ValueError("ENCRYPTION_KEY_BASE64 must be a valid base64 string") from e
                
            if len(key) != 32:
                raise ValueError("ENCRYPTION_KEY_BASE64 must decode to exactly 32 bytes for AES-256-GCM")
                
        jwt_keys = {}
        if jwt_secret:
            jwt_keys["default"] = jwt_secret
        else:
            # Fallback for local dev
            jwt_keys["default"] = "fallback-jwt-secret-do-not-use-in-production"
                
        return cls(encryption_key=key, bcrypt_rounds=rounds, jwt_keys=jwt_keys)
