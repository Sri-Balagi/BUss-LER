import pytest
from app.bootstrap.container import reset_container_for_testing

@pytest.fixture(autouse=True)
def reset_di_container():
    """
    Automatically resets the global Dependency Injection container
    after every test to prevent 'Container has already been built' errors
    during E2E and integration tests.
    """
    yield
    reset_container_for_testing()
