"""Dependency Injection container setup."""

from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")


class ContainerNotInitializedError(RuntimeError):
    """Raised when get_container() is called before build_container()."""

    pass


class Container:
    """A type-safe Dependency Injection container acting as the composition root."""

    def __init__(self) -> None:
        self._singletons: dict[type[Any], Any] = {}
        self._factories: dict[type[Any], Callable[[Container], Any]] = {}
        self._overrides: dict[type[Any], Any] = {}

        # Track active resolution path to detect circular dependencies
        self._resolving: set[type[Any]] = set()

    def register_singleton(self, interface: type[T], instance: T) -> None:
        """Register a pre-instantiated singleton."""
        self._singletons[interface] = instance

    def register_factory(self, interface: type[T], factory: Callable[["Container"], T]) -> None:
        """Register a factory function that will be called when resolving."""
        self._factories[interface] = factory

    def register_scoped(self, interface: type[T], factory: Callable[["Container"], T]) -> None:
        """Reserve scoped registration for Wave 2."""
        raise NotImplementedError("Wave 2")

    def override(self, interface: type[T], instance: T) -> None:
        """Override a dependency for testing purposes."""
        self._overrides[interface] = instance

    def resolve(self, interface: type[T]) -> T:
        """Resolve a dependency from the container."""
        if interface in self._overrides:
            return self._overrides[interface]

        if interface in self._singletons:
            return self._singletons[interface]

        if interface in self._factories:
            if interface in self._resolving:
                raise RecursionError(
                    f"Circular dependency detected while resolving {interface.__name__}"
                )

            self._resolving.add(interface)
            try:
                # We enforce singletons even for factories for now, unless scoped is needed
                instance = self._factories[interface](self)
                self._singletons[interface] = instance
                return instance
            finally:
                self._resolving.remove(interface)

        raise KeyError(f"Service {interface.__name__} not registered in container")

    def resolve_scoped(self, interface: type[T]) -> T:
        """Reserve scoped resolution for Wave 2."""
        raise NotImplementedError("Wave 2")


_global_container: Container | None = None


def build_container() -> Container:
    """Builds and wires the application container. Should be called exactly once during startup."""
    global _global_container
    if _global_container is not None:
        raise RuntimeError("Container has already been built.")

    container = Container()

    # Wire platform dependencies
    from app.runtime.core.di import register_platform_dependencies

    register_platform_dependencies(container)

    _global_container = container
    return _global_container


def get_container() -> Container:
    """Retrieve the built application container.

    Raises:
        ContainerNotInitializedError: If build_container() has not been called.
    """
    if _global_container is None:
        raise ContainerNotInitializedError(
            "build_container() must be called before accessing the container."
        )
    return _global_container


def reset_container_for_testing() -> None:
    """Test helper to clear the global container state."""
    global _global_container
    _global_container = None
