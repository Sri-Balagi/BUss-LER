import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.domain.security.interfaces import IEncryptor

class AES256GCMEncryptor(IEncryptor):
    """
    Implementation of IEncryptor using AES-256-GCM.
    Expects a 32-byte key.
    """
    
    def __init__(self, key: bytes):
        if len(key) != 32:
            raise ValueError("AES-256-GCM requires a 32-byte key.")
        self._aesgcm = AESGCM(key)
        
    def encrypt(self, data: str) -> str:
        """
        Encrypts the plaintext. Returns a base64 encoded string containing the nonce and ciphertext.
        """
        nonce = os.urandom(12)  # Standard nonce size for AES-GCM is 12 bytes
        plaintext_bytes = data.encode('utf-8')
        
        ciphertext = self._aesgcm.encrypt(nonce, plaintext_bytes, None)
        
        # Prepend nonce to ciphertext and base64 encode
        combined = nonce + ciphertext
        return base64.b64encode(combined).decode('utf-8')
        
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypts the base64 encoded ciphertext.
        """
        try:
            combined = base64.b64decode(encrypted_data)
            nonce = combined[:12]
            ciphertext = combined[12:]
            
            plaintext_bytes = self._aesgcm.decrypt(nonce, ciphertext, None)
            return plaintext_bytes.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}") from e
