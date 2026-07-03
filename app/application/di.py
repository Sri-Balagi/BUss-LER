"""Application Layer Dependency Injection Wiring."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.bootstrap.container import Container


def register_application_dependencies(container: "Container") -> None:
    """Wire Application Layer Use Cases into the global DI container."""
    from supabase import AsyncClient

    # Entity Use Cases
    from app.application.entity.create_entity import CreateEntityUseCase
    from app.application.entity.delete_entity import DeleteEntityUseCase
    from app.application.entity.get_entity import GetEntityUseCase
    from app.application.entity.list_entities import ListEntitiesUseCase
    from app.application.entity.update_entity import UpdateEntityUseCase
    from app.infrastructure.persistence.postgres.repositories.entity_repository import (
        EntityRepository,
    )

    def build_entity_repo(c: "Container") -> EntityRepository:
        return EntityRepository(client=c.resolve(AsyncClient))

    # Repositories (if not already registered elsewhere)
    container.register_factory(EntityRepository, build_entity_repo)

    # Use Cases
    container.register_factory(
        CreateEntityUseCase, lambda c: CreateEntityUseCase(c.resolve(EntityRepository))
    )
    container.register_factory(
        GetEntityUseCase, lambda c: GetEntityUseCase(c.resolve(EntityRepository))
    )
    container.register_factory(
        ListEntitiesUseCase, lambda c: ListEntitiesUseCase(c.resolve(EntityRepository))
    )
    container.register_factory(
        UpdateEntityUseCase, lambda c: UpdateEntityUseCase(c.resolve(EntityRepository))
    )
    container.register_factory(
        DeleteEntityUseCase, lambda c: DeleteEntityUseCase(c.resolve(EntityRepository))
    )

    # Twin Use Cases
    from app.application.twin.create_twin import CreateTwinUseCase
    from app.application.twin.delete_twin import DeleteTwinUseCase
    from app.application.twin.get_twin import GetTwinUseCase
    from app.application.twin.list_twins import ListTwinsUseCase
    from app.application.twin.update_twin import UpdateTwinUseCase
    from app.application.twin.get_snapshots import GetTwinSnapshotsUseCase
    from app.application.twin.get_history import GetTwinHistoryUseCase
    from app.infrastructure.persistence.postgres.repositories.twin_repository import (
        TwinRepository,
    )
    from app.infrastructure.persistence.postgres.repositories.snapshot_repository import (
        SnapshotRepository,
    )
    from app.infrastructure.persistence.postgres.repositories.history_repository import (
        HistoryRepository,
    )

    def build_twin_repo(c: "Container") -> TwinRepository:
        return TwinRepository(client=c.resolve(AsyncClient))

    def build_snapshot_repo(c: "Container") -> SnapshotRepository:
        return SnapshotRepository(client=c.resolve(AsyncClient))

    def build_history_repo(c: "Container") -> HistoryRepository:
        return HistoryRepository(client=c.resolve(AsyncClient))

    container.register_factory(TwinRepository, build_twin_repo)
    container.register_factory(SnapshotRepository, build_snapshot_repo)
    container.register_factory(HistoryRepository, build_history_repo)

    container.register_factory(
        CreateTwinUseCase, lambda c: CreateTwinUseCase(c.resolve(TwinRepository), c.resolve(EntityRepository))
    )
    container.register_factory(
        GetTwinUseCase, lambda c: GetTwinUseCase(c.resolve(TwinRepository))
    )
    container.register_factory(
        ListTwinsUseCase, lambda c: ListTwinsUseCase(c.resolve(TwinRepository))
    )
    container.register_factory(
        UpdateTwinUseCase, lambda c: UpdateTwinUseCase(c.resolve(TwinRepository))
    )
    container.register_factory(
        DeleteTwinUseCase, lambda c: DeleteTwinUseCase(c.resolve(TwinRepository))
    )
    container.register_factory(
        GetTwinSnapshotsUseCase, lambda c: GetTwinSnapshotsUseCase(c.resolve(SnapshotRepository))
    )
    container.register_factory(
        GetTwinHistoryUseCase, lambda c: GetTwinHistoryUseCase(c.resolve(HistoryRepository))
    )

