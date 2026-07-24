from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from app.domain.security.models import AuthenticationResult, AuthorizationDecision, ExecutionContext
from app.domain.security.permissions import SystemPermission

if TYPE_CHECKING:
    from app.domain.security.models import SandboxPolicy
    from app.shared.events.models import AuditEvent


class IHasher(ABC):
    """Interface for hashing passwords, API keys, or other secrets."""

    @abstractmethod
    def hash(self, secret: str) -> str:
        """Hashes the given secret."""
        pass

    @abstractmethod
    def verify(self, secret: str, hashed_secret: str) -> bool:
        """Verifies a secret against a hash."""
        pass


class IEncryptor(ABC):
    """Interface for symmetric encryption of data."""

    @abstractmethod
    def encrypt(self, data: str) -> str:
        """Encrypts the given plaintext data. Returns base64 encoded ciphertext."""
        pass

    @abstractmethod
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypts the given base64 encoded ciphertext."""
        pass


class ITokenGenerator(ABC):
    """Interface for generating secure random tokens."""

    @abstractmethod
    def generate_token(self, length: int | None = None) -> str:
        """Generates a secure random token. Uses default length if not specified."""
        pass


class IKeyRotator(ABC):
    """
    Interface for managing encryption key rotation.

    Note: This is a planned capability for a future milestone (e.g., when key versioning
    and KMS integration are introduced). It is defined here to reserve the architectural boundary.
    """

    @abstractmethod
    def rotate_keys(self) -> None:
        """Rotates the primary encryption key."""
        pass


class IIdentityProvider(ABC):
    """
    Interface for Identity Providers (e.g., JWT, API Key, OAuth).
    Responsible for validating a given credential/token and returning the execution context.
    """

    @property
    @abstractmethod
    def scheme(self) -> str:
        """The authentication scheme this provider supports (e.g., 'Bearer', 'ApiKey')."""
        pass

    @abstractmethod
    async def authenticate(self, credentials: str) -> AuthenticationResult:
        """Validates the credentials and returns the AuthenticationResult."""
        pass


class IAuthenticationService(ABC):
    """
    Orchestrating service that delegates credential validation to the appropriate
    IIdentityProvider based on the scheme.
    """

    @abstractmethod
    async def authenticate(self, scheme: str, credentials: str) -> AuthenticationResult:
        """
        Authenticates the request and returns the AuthenticationResult.
        """
        pass


class IPolicyRepository(ABC):
    """
    Interface for looking up policy definitions and resolving roles to permissions.
    """

    @abstractmethod
    async def get_permissions_for_roles(self, roles: list[str]) -> set[str]:
        """Resolves a list of roles into a flattened set of permissions."""
        pass


class IPolicyEngine(ABC):
    """
    Interface for evaluating ExecutionContexts against permissions and policies.
    """

    @abstractmethod
    async def authorize(
        self,
        context: ExecutionContext,
        permission: SystemPermission,
        resource: Any | None = None
    ) -> AuthorizationDecision:
        """
        Evaluates whether the given context has the required permission.
        Optionally takes a resource for fine-grained resource-level policies.
        """
        pass

class ISandboxPolicyEnforcer(ABC):
    """
    Interface for enforcing a SandboxPolicy during execution.
    This separates the execution strategy from the security enforcement logic.
    """

    @abstractmethod
    def enforce(self, policy: SandboxPolicy) -> None:
        """
        Applies the security boundaries described by the SandboxPolicy.
        Must be called inside the isolated environment/subprocess before user code runs.
        """
        pass


class IAuditPublisher(ABC):
    """
    Abstraction for publishing audit and security events.
    Keeps business services decoupled from the underlying messaging implementation (e.g. EventBus).
    """

    @abstractmethod
    def publish_audit(self, event: AuditEvent) -> None:
        """Publishes an audit event asynchronously."""
        pass


class IAuditSink(ABC):
    """
    Abstraction for an audit log storage destination (e.g., PostgreSQL, SIEM, stdout).
    """

    @abstractmethod
    async def record(self, event: AuditEvent) -> None:
        """Persists or forwards the audit event."""
        pass
