import os
import pytest
from app.bootstrap.container import reset_container_for_testing

# Ensure APP_ENV is set to test before tests run
os.environ["APP_ENV"] = "test"
# In case tests need a dummy key to bypass production validation
os.environ.setdefault("ENCRYPTION_KEY_BASE64", "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=")

@pytest.fixture(autouse=True)
def reset_di_container():
    """
    Automatically resets the global Dependency Injection container
    after every test to prevent 'Container has already been built' errors
    during E2E and integration tests.
    """
    yield
    reset_container_for_testing()
