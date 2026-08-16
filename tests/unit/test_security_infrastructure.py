import base64
import os

import bcrypt
import pytest

from app.application.security.crypto_service import CryptographyService
from app.domain.security.interfaces import IEncryptor, IHasher, ITokenGenerator
from app.infrastructure.security.encryptors import AES256GCMEncryptor
from app.infrastructure.security.hashers import BcryptHasher
from app.infrastructure.security.tokens import CSPRNGTokenGenerator


def test_bcrypt_hasher():
    """Test the BcryptHasher."""
    hasher = BcryptHasher(rounds=4)  # Use low rounds for faster testing
    secret = "my_super_secret_password"

    hashed = hasher.hash(secret)
    assert hashed != secret
    assert hashed.startswith("$2b$")

    assert hasher.verify(secret, hashed) is True
    assert hasher.verify("wrong_password", hashed) is False

def test_aes256_gcm_encryptor():
    """Test the AES256GCMEncryptor."""
    key = os.urandom(32)
    encryptor = AES256GCMEncryptor(key=key)

    plaintext = "Confidential Data 123!"
    ciphertext = encryptor.encrypt(plaintext)

    assert ciphertext != plaintext

    decrypted = encryptor.decrypt(ciphertext)
    assert decrypted == plaintext

def test_aes256_gcm_encryptor_invalid_key():
    """Test encryptor initialization with invalid key."""
    with pytest.raises(ValueError, match="requires a 32-byte key"):
        AES256GCMEncryptor(key=os.urandom(16))

def test_aes256_gcm_encryptor_tampering():
    """Test that tampering with ciphertext causes decryption failure."""
    key = os.urandom(32)
    encryptor = AES256GCMEncryptor(key=key)
    ciphertext = encryptor.encrypt("data")

    # Tamper with the base64 encoded string
    tampered = ciphertext[:-4] + "AAAA"
    with pytest.raises(ValueError, match="Decryption failed"):
        encryptor.decrypt(tampered)

def test_csprng_token_generator():
    """Test the token generator."""
    generator = CSPRNGTokenGenerator()
    token = generator.generate_token(16)

    assert isinstance(token, str)
    assert len(token) == 32  # 16 bytes = 32 hex chars

def test_cryptography_service():
    """Test the integrated CryptographyService."""
    key = os.urandom(32)
    service = CryptographyService(
        hasher=BcryptHasher(rounds=4),
        encryptor=AES256GCMEncryptor(key=key),
        token_generator=CSPRNGTokenGenerator()
    )

    # Test hashing
    secret = "foo"
    hashed = service.hash_secret(secret)
    assert service.verify_secret(secret, hashed) is True

    # Test encryption
    data = "bar"
    encrypted = service.encrypt_data(data)
    assert service.decrypt_data(encrypted) == data

    # Test tokens
    token = service.generate_token(8)
    assert len(token) == 16
