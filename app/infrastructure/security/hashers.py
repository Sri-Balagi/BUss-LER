import bcrypt
from app.domain.security.interfaces import IHasher

class BcryptHasher(IHasher):
    """Implementation of IHasher using bcrypt."""
    
    def __init__(self, rounds: int = 12):
        self.rounds = rounds
        
    def hash(self, secret: str) -> str:
        """Hashes the given secret."""
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed_bytes = bcrypt.hashpw(secret.encode('utf-8'), salt)
        return hashed_bytes.decode('utf-8')
        
    def verify(self, secret: str, hashed_secret: str) -> bool:
        """Verifies a secret against a hash."""
        try:
            return bcrypt.checkpw(secret.encode('utf-8'), hashed_secret.encode('utf-8'))
        except ValueError:
            return False
