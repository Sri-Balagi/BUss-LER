"""Entity Service — Orchestrates Entity operations.

Handles business logic for the Entity lifecycle.
"""

from uuid import UUID

import structlog
from app.models.entity import EntityUpdate
from app.models.exceptions import EntityNotFoundError
from app.models.schemas import Entity, EntityCreate
from app.repositories.entity_repository import EntityRepository

logger = structlog.get_logger()


from mutmut.mutation.trampoline import MutantDict
from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated

mutants_xǁEntityServiceǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁEntityServiceǁget_by_id__mutmut: MutantDict = {}  # type: ignore
mutants_xǁEntityServiceǁlist_active__mutmut: MutantDict = {}  # type: ignore
mutants_xǁEntityServiceǁcreate_entity__mutmut: MutantDict = {}  # type: ignore
mutants_xǁEntityServiceǁupdate__mutmut: MutantDict = {}  # type: ignore
mutants_xǁEntityServiceǁdelete__mutmut: MutantDict = {}  # type: ignore


class EntityService:
    """Business logic layer for Entities."""

    @_mutmut_mutated(mutants_xǁEntityServiceǁ__init____mutmut)
    def __init__(
        self,
        entity_repo: EntityRepository,
    ) -> None:
        self._entity_repo = entity_repo

    def xǁEntityServiceǁ__init____mutmut_orig(
        self,
        entity_repo: EntityRepository,
    ) -> None:
        self._entity_repo = entity_repo

    def xǁEntityServiceǁ__init____mutmut_1(
        self,
        entity_repo: EntityRepository,
    ) -> None:
        self._entity_repo = None

    @_mutmut_mutated(mutants_xǁEntityServiceǁget_by_id__mutmut)
    async def get_by_id(self, entity_id: UUID) -> Entity:
        """Fetch an entity by its ID.

        Enforces business rules (e.g. only returning active entities).
        """
        entity = await self._entity_repo.get_by_id(entity_id)
        if not entity.is_active:
            raise EntityNotFoundError(str(entity_id))
        return entity

    async def xǁEntityServiceǁget_by_id__mutmut_orig(self, entity_id: UUID) -> Entity:
        """Fetch an entity by its ID.

        Enforces business rules (e.g. only returning active entities).
        """
        entity = await self._entity_repo.get_by_id(entity_id)
        if not entity.is_active:
            raise EntityNotFoundError(str(entity_id))
        return entity

    async def xǁEntityServiceǁget_by_id__mutmut_1(self, entity_id: UUID) -> Entity:
        """Fetch an entity by its ID.

        Enforces business rules (e.g. only returning active entities).
        """
        entity = None
        if not entity.is_active:
            raise EntityNotFoundError(str(entity_id))
        return entity

    async def xǁEntityServiceǁget_by_id__mutmut_2(self, entity_id: UUID) -> Entity:
        """Fetch an entity by its ID.

        Enforces business rules (e.g. only returning active entities).
        """
        entity = await self._entity_repo.get_by_id(None)
        if not entity.is_active:
            raise EntityNotFoundError(str(entity_id))
        return entity

    async def xǁEntityServiceǁget_by_id__mutmut_3(self, entity_id: UUID) -> Entity:
        """Fetch an entity by its ID.

        Enforces business rules (e.g. only returning active entities).
        """
        entity = await self._entity_repo.get_by_id(entity_id)
        if entity.is_active:
            raise EntityNotFoundError(str(entity_id))
        return entity

    async def xǁEntityServiceǁget_by_id__mutmut_4(self, entity_id: UUID) -> Entity:
        """Fetch an entity by its ID.

        Enforces business rules (e.g. only returning active entities).
        """
        entity = await self._entity_repo.get_by_id(entity_id)
        if not entity.is_active:
            raise EntityNotFoundError(None)
        return entity

    async def xǁEntityServiceǁget_by_id__mutmut_5(self, entity_id: UUID) -> Entity:
        """Fetch an entity by its ID.

        Enforces business rules (e.g. only returning active entities).
        """
        entity = await self._entity_repo.get_by_id(entity_id)
        if not entity.is_active:
            raise EntityNotFoundError(str(None))
        return entity

    @_mutmut_mutated(mutants_xǁEntityServiceǁlist_active__mutmut)
    async def list_active(
        self,
        user_id: UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Entity], int]:
        """List all active entities."""
        return await self._entity_repo.list(
            user_id=user_id,
            is_active=True,
            limit=limit,
            offset=offset,
        )

    async def xǁEntityServiceǁlist_active__mutmut_orig(
        self,
        user_id: UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Entity], int]:
        """List all active entities."""
        return await self._entity_repo.list(
            user_id=user_id,
            is_active=True,
            limit=limit,
            offset=offset,
        )

    async def xǁEntityServiceǁlist_active__mutmut_1(
        self,
        user_id: UUID | None = None,
        limit: int = 21,
        offset: int = 0,
    ) -> tuple[list[Entity], int]:
        """List all active entities."""
        return await self._entity_repo.list(
            user_id=user_id,
            is_active=True,
            limit=limit,
            offset=offset,
        )

    async def xǁEntityServiceǁlist_active__mutmut_2(
        self,
        user_id: UUID | None = None,
        limit: int = 20,
        offset: int = 1,
    ) -> tuple[list[Entity], int]:
        """List all active entities."""
        return await self._entity_repo.list(
            user_id=user_id,
            is_active=True,
            limit=limit,
            offset=offset,
        )

    async def xǁEntityServiceǁlist_active__mutmut_3(
        self,
        user_id: UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Entity], int]:
        """List all active entities."""
        return await self._entity_repo.list(
            user_id=None,
            is_active=True,
            limit=limit,
            offset=offset,
        )

    async def xǁEntityServiceǁlist_active__mutmut_4(
        self,
        user_id: UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Entity], int]:
        """List all active entities."""
        return await self._entity_repo.list(
            user_id=user_id,
            is_active=None,
            limit=limit,
            offset=offset,
        )

    async def xǁEntityServiceǁlist_active__mutmut_5(
        self,
        user_id: UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Entity], int]:
        """List all active entities."""
        return await self._entity_repo.list(
            user_id=user_id,
            is_active=True,
            limit=None,
            offset=offset,
        )

    async def xǁEntityServiceǁlist_active__mutmut_6(
        self,
        user_id: UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Entity], int]:
        """List all active entities."""
        return await self._entity_repo.list(
            user_id=user_id,
            is_active=True,
            limit=limit,
            offset=None,
        )

    async def xǁEntityServiceǁlist_active__mutmut_7(
        self,
        user_id: UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Entity], int]:
        """List all active entities."""
        return await self._entity_repo.list(
            is_active=True,
            limit=limit,
            offset=offset,
        )

    async def xǁEntityServiceǁlist_active__mutmut_8(
        self,
        user_id: UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Entity], int]:
        """List all active entities."""
        return await self._entity_repo.list(
            user_id=user_id,
            limit=limit,
            offset=offset,
        )

    async def xǁEntityServiceǁlist_active__mutmut_9(
        self,
        user_id: UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Entity], int]:
        """List all active entities."""
        return await self._entity_repo.list(
            user_id=user_id,
            is_active=True,
            offset=offset,
        )

    async def xǁEntityServiceǁlist_active__mutmut_10(
        self,
        user_id: UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Entity], int]:
        """List all active entities."""
        return await self._entity_repo.list(
            user_id=user_id,
            is_active=True,
            limit=limit,
        )

    async def xǁEntityServiceǁlist_active__mutmut_11(
        self,
        user_id: UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Entity], int]:
        """List all active entities."""
        return await self._entity_repo.list(
            user_id=user_id,
            is_active=False,
            limit=limit,
            offset=offset,
        )

    @_mutmut_mutated(mutants_xǁEntityServiceǁcreate_entity__mutmut)
    async def create_entity(self, user_id: UUID, data: EntityCreate) -> Entity:
        """Create a new entity.

        Args:
            user_id: The authenticated user owning the entity.
            data: Entity creation payload.

        Returns:
            The created entity.
        """
        logger.info("Creating entity", user_id=str(user_id))
        return await self._entity_repo.create(user_id, data)

    async def xǁEntityServiceǁcreate_entity__mutmut_orig(
        self, user_id: UUID, data: EntityCreate
    ) -> Entity:
        """Create a new entity.

        Args:
            user_id: The authenticated user owning the entity.
            data: Entity creation payload.

        Returns:
            The created entity.
        """
        logger.info("Creating entity", user_id=str(user_id))
        return await self._entity_repo.create(user_id, data)

    async def xǁEntityServiceǁcreate_entity__mutmut_1(
        self, user_id: UUID, data: EntityCreate
    ) -> Entity:
        """Create a new entity.

        Args:
            user_id: The authenticated user owning the entity.
            data: Entity creation payload.

        Returns:
            The created entity.
        """
        logger.info(None, user_id=str(user_id))
        return await self._entity_repo.create(user_id, data)

    async def xǁEntityServiceǁcreate_entity__mutmut_2(
        self, user_id: UUID, data: EntityCreate
    ) -> Entity:
        """Create a new entity.

        Args:
            user_id: The authenticated user owning the entity.
            data: Entity creation payload.

        Returns:
            The created entity.
        """
        logger.info("Creating entity", user_id=None)
        return await self._entity_repo.create(user_id, data)

    async def xǁEntityServiceǁcreate_entity__mutmut_3(
        self, user_id: UUID, data: EntityCreate
    ) -> Entity:
        """Create a new entity.

        Args:
            user_id: The authenticated user owning the entity.
            data: Entity creation payload.

        Returns:
            The created entity.
        """
        logger.info(user_id=str(user_id))
        return await self._entity_repo.create(user_id, data)

    async def xǁEntityServiceǁcreate_entity__mutmut_4(
        self, user_id: UUID, data: EntityCreate
    ) -> Entity:
        """Create a new entity.

        Args:
            user_id: The authenticated user owning the entity.
            data: Entity creation payload.

        Returns:
            The created entity.
        """
        logger.info(
            "Creating entity",
        )
        return await self._entity_repo.create(user_id, data)

    async def xǁEntityServiceǁcreate_entity__mutmut_5(
        self, user_id: UUID, data: EntityCreate
    ) -> Entity:
        """Create a new entity.

        Args:
            user_id: The authenticated user owning the entity.
            data: Entity creation payload.

        Returns:
            The created entity.
        """
        logger.info("XXCreating entityXX", user_id=str(user_id))
        return await self._entity_repo.create(user_id, data)

    async def xǁEntityServiceǁcreate_entity__mutmut_6(
        self, user_id: UUID, data: EntityCreate
    ) -> Entity:
        """Create a new entity.

        Args:
            user_id: The authenticated user owning the entity.
            data: Entity creation payload.

        Returns:
            The created entity.
        """
        logger.info("creating entity", user_id=str(user_id))
        return await self._entity_repo.create(user_id, data)

    async def xǁEntityServiceǁcreate_entity__mutmut_7(
        self, user_id: UUID, data: EntityCreate
    ) -> Entity:
        """Create a new entity.

        Args:
            user_id: The authenticated user owning the entity.
            data: Entity creation payload.

        Returns:
            The created entity.
        """
        logger.info("CREATING ENTITY", user_id=str(user_id))
        return await self._entity_repo.create(user_id, data)

    async def xǁEntityServiceǁcreate_entity__mutmut_8(
        self, user_id: UUID, data: EntityCreate
    ) -> Entity:
        """Create a new entity.

        Args:
            user_id: The authenticated user owning the entity.
            data: Entity creation payload.

        Returns:
            The created entity.
        """
        logger.info("Creating entity", user_id=str(None))
        return await self._entity_repo.create(user_id, data)

    async def xǁEntityServiceǁcreate_entity__mutmut_9(
        self, user_id: UUID, data: EntityCreate
    ) -> Entity:
        """Create a new entity.

        Args:
            user_id: The authenticated user owning the entity.
            data: Entity creation payload.

        Returns:
            The created entity.
        """
        logger.info("Creating entity", user_id=str(user_id))
        return await self._entity_repo.create(None, data)

    async def xǁEntityServiceǁcreate_entity__mutmut_10(
        self, user_id: UUID, data: EntityCreate
    ) -> Entity:
        """Create a new entity.

        Args:
            user_id: The authenticated user owning the entity.
            data: Entity creation payload.

        Returns:
            The created entity.
        """
        logger.info("Creating entity", user_id=str(user_id))
        return await self._entity_repo.create(user_id, None)

    async def xǁEntityServiceǁcreate_entity__mutmut_11(
        self, user_id: UUID, data: EntityCreate
    ) -> Entity:
        """Create a new entity.

        Args:
            user_id: The authenticated user owning the entity.
            data: Entity creation payload.

        Returns:
            The created entity.
        """
        logger.info("Creating entity", user_id=str(user_id))
        return await self._entity_repo.create(data)

    async def xǁEntityServiceǁcreate_entity__mutmut_12(
        self, user_id: UUID, data: EntityCreate
    ) -> Entity:
        """Create a new entity.

        Args:
            user_id: The authenticated user owning the entity.
            data: Entity creation payload.

        Returns:
            The created entity.
        """
        logger.info("Creating entity", user_id=str(user_id))
        return await self._entity_repo.create(
            user_id,
        )

    @_mutmut_mutated(mutants_xǁEntityServiceǁupdate__mutmut)
    async def update(self, entity_id: UUID, data: EntityUpdate) -> Entity:
        """Update an entity.

        Ensures the entity exists and is active before updating.
        """
        # Enforce active check
        await self.get_by_id(entity_id)

        return await self._entity_repo.update(entity_id, data)

    async def xǁEntityServiceǁupdate__mutmut_orig(
        self, entity_id: UUID, data: EntityUpdate
    ) -> Entity:
        """Update an entity.

        Ensures the entity exists and is active before updating.
        """
        # Enforce active check
        await self.get_by_id(entity_id)

        return await self._entity_repo.update(entity_id, data)

    async def xǁEntityServiceǁupdate__mutmut_1(self, entity_id: UUID, data: EntityUpdate) -> Entity:
        """Update an entity.

        Ensures the entity exists and is active before updating.
        """
        # Enforce active check
        await self.get_by_id(None)

        return await self._entity_repo.update(entity_id, data)

    async def xǁEntityServiceǁupdate__mutmut_2(self, entity_id: UUID, data: EntityUpdate) -> Entity:
        """Update an entity.

        Ensures the entity exists and is active before updating.
        """
        # Enforce active check
        await self.get_by_id(entity_id)

        return await self._entity_repo.update(None, data)

    async def xǁEntityServiceǁupdate__mutmut_3(self, entity_id: UUID, data: EntityUpdate) -> Entity:
        """Update an entity.

        Ensures the entity exists and is active before updating.
        """
        # Enforce active check
        await self.get_by_id(entity_id)

        return await self._entity_repo.update(entity_id, None)

    async def xǁEntityServiceǁupdate__mutmut_4(self, entity_id: UUID, data: EntityUpdate) -> Entity:
        """Update an entity.

        Ensures the entity exists and is active before updating.
        """
        # Enforce active check
        await self.get_by_id(entity_id)

        return await self._entity_repo.update(data)

    async def xǁEntityServiceǁupdate__mutmut_5(self, entity_id: UUID, data: EntityUpdate) -> Entity:
        """Update an entity.

        Ensures the entity exists and is active before updating.
        """
        # Enforce active check
        await self.get_by_id(entity_id)

        return await self._entity_repo.update(
            entity_id,
        )

    @_mutmut_mutated(mutants_xǁEntityServiceǁdelete__mutmut)
    async def delete(self, entity_id: UUID) -> None:
        """Soft-delete an entity."""
        # Enforce active check
        await self.get_by_id(entity_id)

        await self._entity_repo.soft_delete(entity_id)

    async def xǁEntityServiceǁdelete__mutmut_orig(self, entity_id: UUID) -> None:
        """Soft-delete an entity."""
        # Enforce active check
        await self.get_by_id(entity_id)

        await self._entity_repo.soft_delete(entity_id)

    async def xǁEntityServiceǁdelete__mutmut_1(self, entity_id: UUID) -> None:
        """Soft-delete an entity."""
        # Enforce active check
        await self.get_by_id(None)

        await self._entity_repo.soft_delete(entity_id)

    async def xǁEntityServiceǁdelete__mutmut_2(self, entity_id: UUID) -> None:
        """Soft-delete an entity."""
        # Enforce active check
        await self.get_by_id(entity_id)

        await self._entity_repo.soft_delete(None)


mutants_xǁEntityServiceǁ__init____mutmut["_mutmut_orig"] = (
    EntityService.xǁEntityServiceǁ__init____mutmut_orig
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁ__init____mutmut["xǁEntityServiceǁ__init____mutmut_1"] = (
    EntityService.xǁEntityServiceǁ__init____mutmut_1
)  # type: ignore # mutmut generated

mutants_xǁEntityServiceǁget_by_id__mutmut["_mutmut_orig"] = (
    EntityService.xǁEntityServiceǁget_by_id__mutmut_orig
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁget_by_id__mutmut["xǁEntityServiceǁget_by_id__mutmut_1"] = (
    EntityService.xǁEntityServiceǁget_by_id__mutmut_1
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁget_by_id__mutmut["xǁEntityServiceǁget_by_id__mutmut_2"] = (
    EntityService.xǁEntityServiceǁget_by_id__mutmut_2
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁget_by_id__mutmut["xǁEntityServiceǁget_by_id__mutmut_3"] = (
    EntityService.xǁEntityServiceǁget_by_id__mutmut_3
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁget_by_id__mutmut["xǁEntityServiceǁget_by_id__mutmut_4"] = (
    EntityService.xǁEntityServiceǁget_by_id__mutmut_4
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁget_by_id__mutmut["xǁEntityServiceǁget_by_id__mutmut_5"] = (
    EntityService.xǁEntityServiceǁget_by_id__mutmut_5
)  # type: ignore # mutmut generated

mutants_xǁEntityServiceǁlist_active__mutmut["_mutmut_orig"] = (
    EntityService.xǁEntityServiceǁlist_active__mutmut_orig
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁlist_active__mutmut["xǁEntityServiceǁlist_active__mutmut_1"] = (
    EntityService.xǁEntityServiceǁlist_active__mutmut_1
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁlist_active__mutmut["xǁEntityServiceǁlist_active__mutmut_2"] = (
    EntityService.xǁEntityServiceǁlist_active__mutmut_2
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁlist_active__mutmut["xǁEntityServiceǁlist_active__mutmut_3"] = (
    EntityService.xǁEntityServiceǁlist_active__mutmut_3
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁlist_active__mutmut["xǁEntityServiceǁlist_active__mutmut_4"] = (
    EntityService.xǁEntityServiceǁlist_active__mutmut_4
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁlist_active__mutmut["xǁEntityServiceǁlist_active__mutmut_5"] = (
    EntityService.xǁEntityServiceǁlist_active__mutmut_5
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁlist_active__mutmut["xǁEntityServiceǁlist_active__mutmut_6"] = (
    EntityService.xǁEntityServiceǁlist_active__mutmut_6
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁlist_active__mutmut["xǁEntityServiceǁlist_active__mutmut_7"] = (
    EntityService.xǁEntityServiceǁlist_active__mutmut_7
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁlist_active__mutmut["xǁEntityServiceǁlist_active__mutmut_8"] = (
    EntityService.xǁEntityServiceǁlist_active__mutmut_8
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁlist_active__mutmut["xǁEntityServiceǁlist_active__mutmut_9"] = (
    EntityService.xǁEntityServiceǁlist_active__mutmut_9
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁlist_active__mutmut["xǁEntityServiceǁlist_active__mutmut_10"] = (
    EntityService.xǁEntityServiceǁlist_active__mutmut_10
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁlist_active__mutmut["xǁEntityServiceǁlist_active__mutmut_11"] = (
    EntityService.xǁEntityServiceǁlist_active__mutmut_11
)  # type: ignore # mutmut generated

mutants_xǁEntityServiceǁcreate_entity__mutmut["_mutmut_orig"] = (
    EntityService.xǁEntityServiceǁcreate_entity__mutmut_orig
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁcreate_entity__mutmut["xǁEntityServiceǁcreate_entity__mutmut_1"] = (
    EntityService.xǁEntityServiceǁcreate_entity__mutmut_1
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁcreate_entity__mutmut["xǁEntityServiceǁcreate_entity__mutmut_2"] = (
    EntityService.xǁEntityServiceǁcreate_entity__mutmut_2
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁcreate_entity__mutmut["xǁEntityServiceǁcreate_entity__mutmut_3"] = (
    EntityService.xǁEntityServiceǁcreate_entity__mutmut_3
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁcreate_entity__mutmut["xǁEntityServiceǁcreate_entity__mutmut_4"] = (
    EntityService.xǁEntityServiceǁcreate_entity__mutmut_4
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁcreate_entity__mutmut["xǁEntityServiceǁcreate_entity__mutmut_5"] = (
    EntityService.xǁEntityServiceǁcreate_entity__mutmut_5
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁcreate_entity__mutmut["xǁEntityServiceǁcreate_entity__mutmut_6"] = (
    EntityService.xǁEntityServiceǁcreate_entity__mutmut_6
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁcreate_entity__mutmut["xǁEntityServiceǁcreate_entity__mutmut_7"] = (
    EntityService.xǁEntityServiceǁcreate_entity__mutmut_7
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁcreate_entity__mutmut["xǁEntityServiceǁcreate_entity__mutmut_8"] = (
    EntityService.xǁEntityServiceǁcreate_entity__mutmut_8
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁcreate_entity__mutmut["xǁEntityServiceǁcreate_entity__mutmut_9"] = (
    EntityService.xǁEntityServiceǁcreate_entity__mutmut_9
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁcreate_entity__mutmut["xǁEntityServiceǁcreate_entity__mutmut_10"] = (
    EntityService.xǁEntityServiceǁcreate_entity__mutmut_10
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁcreate_entity__mutmut["xǁEntityServiceǁcreate_entity__mutmut_11"] = (
    EntityService.xǁEntityServiceǁcreate_entity__mutmut_11
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁcreate_entity__mutmut["xǁEntityServiceǁcreate_entity__mutmut_12"] = (
    EntityService.xǁEntityServiceǁcreate_entity__mutmut_12
)  # type: ignore # mutmut generated

mutants_xǁEntityServiceǁupdate__mutmut["_mutmut_orig"] = (
    EntityService.xǁEntityServiceǁupdate__mutmut_orig
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁupdate__mutmut["xǁEntityServiceǁupdate__mutmut_1"] = (
    EntityService.xǁEntityServiceǁupdate__mutmut_1
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁupdate__mutmut["xǁEntityServiceǁupdate__mutmut_2"] = (
    EntityService.xǁEntityServiceǁupdate__mutmut_2
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁupdate__mutmut["xǁEntityServiceǁupdate__mutmut_3"] = (
    EntityService.xǁEntityServiceǁupdate__mutmut_3
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁupdate__mutmut["xǁEntityServiceǁupdate__mutmut_4"] = (
    EntityService.xǁEntityServiceǁupdate__mutmut_4
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁupdate__mutmut["xǁEntityServiceǁupdate__mutmut_5"] = (
    EntityService.xǁEntityServiceǁupdate__mutmut_5
)  # type: ignore # mutmut generated

mutants_xǁEntityServiceǁdelete__mutmut["_mutmut_orig"] = (
    EntityService.xǁEntityServiceǁdelete__mutmut_orig
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁdelete__mutmut["xǁEntityServiceǁdelete__mutmut_1"] = (
    EntityService.xǁEntityServiceǁdelete__mutmut_1
)  # type: ignore # mutmut generated
mutants_xǁEntityServiceǁdelete__mutmut["xǁEntityServiceǁdelete__mutmut_2"] = (
    EntityService.xǁEntityServiceǁdelete__mutmut_2
)  # type: ignore # mutmut generated
