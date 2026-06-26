"""BizOS domain exceptions.

Centralized exception hierarchy for the Digital Twin System.
These exceptions are raised by the service layer and caught by
the API layer to return appropriate HTTP status codes.

Mapping:
    NotFoundError       -> 404 Not Found
    VersionConflictError -> 409 Conflict
    DuplicateTwinError  -> 409 Conflict
    ValidationError     -> 422 Unprocessable Entity
    RepositoryError     -> 500 Internal Server Error
"""


class BizOSError(Exception):
    """Base exception for all BizOS domain errors."""

    def __init__(self, message: str, detail: str | None = None) -> None:
        self.message = message
        self.detail = detail
        super().__init__(self.message)


# =============================================================================
# Not Found Errors (HTTP 404)
# =============================================================================


class NotFoundError(BizOSError):
    """Raised when a requested resource does not exist."""


class EntityNotFoundError(NotFoundError):
    """Raised when an entity lookup fails."""

    def __init__(self, entity_id: str) -> None:
        super().__init__(
            message=f"Entity not found: {entity_id}",
            detail=f"No entity exists with ID '{entity_id}'.",
        )
        self.entity_id = entity_id


class TwinNotFoundError(NotFoundError):
    """Raised when a Digital Twin lookup fails."""

    def __init__(self, twin_id: str) -> None:
        super().__init__(
            message=f"Digital Twin not found: {twin_id}",
            detail=f"No Digital Twin exists with ID '{twin_id}'.",
        )
        self.twin_id = twin_id


# =============================================================================
# Conflict Errors (HTTP 409)
# =============================================================================


class VersionConflictError(BizOSError):
    """Raised when an optimistic concurrency check fails.

    This occurs when the expected version does not match the current
    version of the resource, indicating a concurrent modification.
    """

    def __init__(self, expected: int, actual: int) -> None:
        super().__init__(
            message=f"Version conflict: expected {expected}, actual {actual}",
            detail=(
                f"The resource was modified by another operation. "
                f"Expected version {expected} but current version is {actual}. "
                f"Reload the resource and retry."
            ),
        )
        self.expected_version = expected
        self.actual_version = actual


class DuplicateTwinError(BizOSError):
    """Raised when attempting to create a twin for an entity that already has one."""

    def __init__(self, entity_id: str) -> None:
        super().__init__(
            message=f"Entity already has a Digital Twin: {entity_id}",
            detail=(
                f"A Digital Twin already exists for entity '{entity_id}'. "
                f"Each entity can have at most one twin."
            ),
        )
        self.entity_id = entity_id


# =============================================================================
# Validation Errors (HTTP 422)
# =============================================================================


class DomainValidationError(BizOSError):
    """Raised when domain validation fails beyond Pydantic field-level checks."""


# =============================================================================
# Infrastructure Errors (HTTP 500)
# =============================================================================


class RepositoryError(BizOSError):
    """Raised when a database operation fails unexpectedly.

    Wraps underlying database client errors so the service layer
    does not need to handle Supabase-specific exceptions.
    """

    def __init__(self, operation: str, detail: str | None = None) -> None:
        super().__init__(
            message=f"Repository operation failed: {operation}",
            detail=detail,
        )
        self.operation = operation


class VectorDatabaseError(RepositoryError):
    """Raised when a Qdrant SDK operation fails.
    
    This abstracts away the underlying HTTP or connection errors
    raised by the Qdrant client.
    """

    def __init__(self, operation: str, detail: str | None = None) -> None:
        super().__init__(
            operation=operation,
            detail=detail or "An unexpected error occurred in the vector database.",
        )


class ServiceError(BizOSError):
    """Raised when a service-level orchestration or business rule fails."""

    def __init__(self, operation: str, detail: str | None = None) -> None:
        super().__init__(
            message=f"Service operation failed: {operation}",
            detail=detail,
        )
        self.operation = operation


class MemoryNotFoundError(BizOSError):
    """Raised when a memory cannot be found."""

    def __init__(self, memory_id: str) -> None:
        super().__init__(
            message=f"Memory not found: {memory_id}",
            detail="The requested memory does not exist or has been permanently deleted.",
        )
        self.memory_id = memory_id


class DuplicateMemoryError(RepositoryError):
    """Raised when a unique constraint on memories is violated."""
    
    def __init__(self, detail: str = "Memory already exists"):
        super().__init__(operation="memory_create", detail=detail)


class AIKernelError(BizOSError):
    """Base exception for all AI Kernel operations."""
    
    def __init__(self, provider: str, operation: str, detail: str):
        super().__init__(
            message=f"AI Kernel ({provider}) failed during {operation}: {detail}",
            detail=detail
        )
        self.provider = provider
        self.operation = operation


class ProviderConfigurationError(AIKernelError):
    """Raised when an AI provider is misconfigured or missing credentials."""
    
    def __init__(self, provider: str, detail: str):
        super().__init__(provider=provider, operation="configuration", detail=detail)
