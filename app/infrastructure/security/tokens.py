import secrets
from app.domain.security.interfaces import ITokenGenerator

class CSPRNGTokenGenerator(ITokenGenerator):
    """
    Implementation of ITokenGenerator using the cryptographically secure
    pseudorandom number generator (CSPRNG) provided by the `secrets` module.
    """
    
    def __init__(self, token_length_bytes: int = 32):
        self._token_length = token_length_bytes
        
    def generate_token(self, length: int | None = None) -> str:
        """
        Generates a secure random token of the specified byte length (or default), returned as a hex string.
        """
        return secrets.token_hex(length or self._token_length)
