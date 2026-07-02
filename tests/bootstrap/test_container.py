import pytest

from app.bootstrap.container import (
    Container,
    ContainerNotInitializedError,
    build_container,
    get_container,
    reset_container_for_testing,
)


class IDependencyA:
    pass


class DependencyA(IDependencyA):
    pass


class IDependencyB:
    pass


class DependencyB(IDependencyB):
    def __init__(self, a: IDependencyA):
        self.a = a


@pytest.fixture(autouse=True)
def reset_container():
    reset_container_for_testing()
    yield
    reset_container_for_testing()


def test_register_and_resolve_singleton():
    container = Container()
    instance = DependencyA()
    container.register_singleton(IDependencyA, instance)

    resolved = container.resolve(IDependencyA)
    assert resolved is instance


def test_register_and_resolve_factory():
    container = Container()

    def factory(c):
        return DependencyA()

    container.register_factory(IDependencyA, factory)

    resolved1 = container.resolve(IDependencyA)
    resolved2 = container.resolve(IDependencyA)

    assert isinstance(resolved1, DependencyA)
    # The container should cache the factory result as a singleton
    assert resolved1 is resolved2


def test_resolve_unregistered_raises_keyerror():
    container = Container()
    with pytest.raises(KeyError, match="Service IDependencyA not registered in container"):
        container.resolve(IDependencyA)


def test_factory_dependency_resolution():
    container = Container()
    container.register_factory(IDependencyA, lambda c: DependencyA())
    container.register_factory(IDependencyB, lambda c: DependencyB(c.resolve(IDependencyA)))

    resolved_b = container.resolve(IDependencyB)
    assert isinstance(resolved_b, DependencyB)
    assert isinstance(resolved_b.a, DependencyA)


def test_override_dependency():
    container = Container()
    container.register_factory(IDependencyA, lambda c: DependencyA())

    mock_instance = DependencyA()
    container.override(IDependencyA, mock_instance)

    assert container.resolve(IDependencyA) is mock_instance


def test_circular_dependency_detection():
    container = Container()
    container.register_factory(IDependencyA, lambda c: c.resolve(IDependencyB))
    container.register_factory(IDependencyB, lambda c: c.resolve(IDependencyA))

    with pytest.raises(RecursionError, match="Circular dependency detected while resolving"):
        container.resolve(IDependencyA)


def test_build_container_singleton():
    with pytest.raises(ContainerNotInitializedError):
        get_container()

    c1 = build_container()
    assert isinstance(c1, Container)

    c2 = get_container()
    assert c1 is c2

    with pytest.raises(RuntimeError, match="Container has already been built"):
        build_container()


def test_scoped_not_implemented():
    container = Container()
    with pytest.raises(NotImplementedError, match="Wave 2"):
        container.register_scoped(IDependencyA, lambda c: DependencyA())

    with pytest.raises(NotImplementedError, match="Wave 2"):
        container.resolve_scoped(IDependencyA)
