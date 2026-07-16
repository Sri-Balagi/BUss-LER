from typing import Optional

from app.domain.security.interfaces import IHasher, IEncryptor, ITokenGenerator, IKeyRotator

class CryptographyService:
    """
    Application service that provides unified cryptographic operations.
    It encapsulates hashing, encryption, token generation, and key rotation.
    All security-related components must depend on this service.
    """
    
    def __init__(
        self,
        hasher: IHasher,
        encryptor: IEncryptor,
        token_generator: ITokenGenerator
    ):
        self._hasher = hasher
        self._encryptor = encryptor
        self._token_generator = token_generator
        
    def hash_secret(self, secret: str) -> str:
        """Hashes a secret (e.g., password, API key)."""
        return self._hasher.hash(secret)
        
    def verify_secret(self, secret: str, hashed_secret: str) -> bool:
        """Verifies a secret against a hash."""
        return self._hasher.verify(secret, hashed_secret)
        
    def encrypt_data(self, data: str) -> str:
        """Encrypts data symmetrically."""
        return self._encryptor.encrypt(data)
        
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypts symmetrically encrypted data."""
        return self._encryptor.decrypt(encrypted_data)
        
    def generate_token(self, length: int | None = None) -> str:
        """Generates a secure random token."""
        return self._token_generator.generate_token(length)
        

