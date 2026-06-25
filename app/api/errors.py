"""Centralized FastAPI exception handlers."""

import structlog
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.models.exceptions import (
    DomainValidationError,
    DuplicateTwinError,
    EntityNotFoundError,
    RepositoryError,
    ServiceError,
    TwinNotFoundError,
    VersionConflictError,
)

logger = structlog.get_logger()


async def entity_not_found_handler(request: Request, exc: EntityNotFoundError) -> JSONResponse:
    logger.warning("Entity not found", url=str(request.url), detail=exc.detail)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message},
    )


async def twin_not_found_handler(request: Request, exc: TwinNotFoundError) -> JSONResponse:
    logger.warning("Twin not found", url=str(request.url), detail=exc.detail)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message},
    )


async def version_conflict_handler(request: Request, exc: VersionConflictError) -> JSONResponse:
    logger.warning("Version conflict", url=str(request.url), detail=exc.detail)
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.message},
    )


async def duplicate_twin_handler(request: Request, exc: DuplicateTwinError) -> JSONResponse:
    logger.warning("Duplicate twin", url=str(request.url), detail=exc.detail)
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.message},
    )


async def domain_validation_handler(request: Request, exc: DomainValidationError) -> JSONResponse:
    logger.warning("Domain validation failed", url=str(request.url), detail=exc.detail)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.message},
    )


async def repository_error_handler(request: Request, exc: RepositoryError) -> JSONResponse:
    logger.error("Repository error", url=str(request.url), detail=exc.detail)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal database error occurred."},
    )


async def service_error_handler(request: Request, exc: ServiceError) -> JSONResponse:
    logger.error("Service error", url=str(request.url), detail=exc.detail)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal service orchestration error occurred."},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all domain exception handlers to the FastAPI app."""
    app.add_exception_handler(EntityNotFoundError, entity_not_found_handler)
    app.add_exception_handler(TwinNotFoundError, twin_not_found_handler)
    app.add_exception_handler(VersionConflictError, version_conflict_handler)
    app.add_exception_handler(DuplicateTwinError, duplicate_twin_handler)
    app.add_exception_handler(DomainValidationError, domain_validation_handler)
    app.add_exception_handler(RepositoryError, repository_error_handler)
    app.add_exception_handler(ServiceError, service_error_handler)
