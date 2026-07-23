"""Dependency Injection container setup."""

from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")


class ContainerNotInitializedError(RuntimeError):
    """Raised when get_container() is called before build_container()."""

    pass


import contextvars

class Container:
    """A type-safe Dependency Injection container acting as the composition root."""

    def __init__(self) -> None:
        self._singletons: dict[type[Any], Any] = {}
        self._factories: dict[type[Any], Callable[[Container], Any]] = {}
        self._scoped_factories: dict[type[Any], Callable[[Container], Any]] = {}
        self._overrides: dict[type[Any], Any] = {}

        # Track active resolution path to detect circular dependencies
        self._resolving: set[type[Any]] = set()
        
        # Scoped instances storage per context
        self._scoped_instances: contextvars.ContextVar[dict[type[Any], Any]] = contextvars.ContextVar(
            "scoped_instances", default={}
        )

    def register_singleton(self, interface: type[T], instance: T) -> None:
        """Register a pre-instantiated singleton."""
        self._singletons[interface] = instance

    def register_factory(self, interface: type[T], factory: Callable[["Container"], T]) -> None:
        """Register a factory function that will be called when resolving."""
        self._factories[interface] = factory

    def register_scoped(self, interface: type[T], factory: Callable[["Container"], T]) -> None:
        """Register a factory that is resolved once per request/context scope."""
        self._scoped_factories[interface] = factory

    def override(self, interface: type[T], instance: T) -> None:
        """Override a dependency for testing purposes."""
        self._overrides[interface] = instance

    def resolve(self, interface: type[T]) -> T:
        """Resolve a dependency from the container."""
        if interface in self._overrides:
            return self._overrides[interface]

        if interface in self._singletons:
            return self._singletons[interface]
            
        if interface in self._scoped_factories:
            return self.resolve_scoped(interface)

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

        name = getattr(interface, "__name__", str(interface))
        raise KeyError(f"Service {name} not registered in container")

    def resolve_scoped(self, interface: type[T]) -> T:
        """Resolve a dependency strictly bound to the current execution context."""
        if interface not in self._scoped_factories:
             raise KeyError(f"Service {interface.__name__} is not registered as scoped.")
             
        scoped_cache = self._scoped_instances.get()
        # If running in a shared mutable dict fallback, make a new dict if it's the default
        if id(scoped_cache) == id(self._scoped_instances.get()):
             pass # contextvars will return the same default object if not explicitly set per task, but this is fine for fallback
             
        if interface in scoped_cache:
            return scoped_cache[interface]
            
        if interface in self._resolving:
            raise RecursionError(
                f"Circular dependency detected while resolving {interface.__name__}"
            )
            
        self._resolving.add(interface)
        try:
            instance = self._scoped_factories[interface](self)
            
            # ContextVar default is mutable so we should explicitly set a new dict if we modify it
            current_cache = self._scoped_instances.get()
            new_cache = current_cache.copy()
            new_cache[interface] = instance
            self._scoped_instances.set(new_cache)
            
            return instance
        finally:
            self._resolving.remove(interface)


_global_container: Container | None = None


def build_container() -> Container:
    """Builds and wires the application container. Should be called exactly once during startup."""
    global _global_container
    if _global_container is not None:
        raise RuntimeError("Container has already been built.")

    container = Container()

    # Register Settings singleton so infrastructure components can resolve it
    from app.config import get_settings, Settings
    settings_instance = get_settings()
    container.register_singleton(Settings, settings_instance)

    # Wire platform dependencies
    from app.runtime.core.di import register_platform_dependencies

    register_platform_dependencies(container)

    # Wire security dependencies
    from app.application.security.di import register_security_dependencies
    register_security_dependencies(container)

    # Wire knowledge dependencies
    from app.application.knowledge.di import register_knowledge_dependencies
    register_knowledge_dependencies(container)

    # Wire memory dependencies
    from app.application.memory.di import register_memory_dependencies
    register_memory_dependencies(container)
    
    # Wire intelligence infrastructure
    from app.application.intelligence.di import register_intelligence_infrastructure
    register_intelligence_infrastructure(container)
    
    # Wire twin dependencies
    from app.application.twin.di import register_twin_dependencies
    register_twin_dependencies(container)
    
    # Wire retrieval dependencies
    from app.application.retrieval.di import register_retrieval_dependencies
    register_retrieval_dependencies(container)

    # Wire reasoning dependencies
    from app.application.reasoning.di import register_reasoning_dependencies
    register_reasoning_dependencies(container)

    # Wire planning dependencies
    from app.application.planning.di import register_planning_dependencies
    register_planning_dependencies(container)
    
    # Wire workflow intelligence
    from app.application.workflow.di import configure_workflow_intelligence
    configure_workflow_intelligence(container)

    # Wire cognition dependencies
    from app.application.cognition.di import configure_cognition_dependencies
    configure_cognition_dependencies(container)

    # Wire learning dependencies
    from app.application.learning.di import register_learning_subsystem
    register_learning_subsystem(container)

    # Wire Wave 6 Application dependencies
    from app.application.applications.di import register_application_services
    register_application_services(container)

    # Wire Wave 7 Notification and Human Interaction Layer
    from app.application.notifications.di import register_notification_dependencies
    register_notification_dependencies(container)

    # Wire Wave 7.5 Agent Foundation
    from app.application.agents.di import register_agent_dependencies
    register_agent_dependencies(container)

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
