import pytest


@pytest.fixture(autouse=True)
def setup_and_teardown_tables():
    """Override the root autouse fixture — scoring engine tests need no database."""
    yield


@pytest.fixture(scope="session")
def db_provider():
    """Override session-scoped DB provider — not needed for pure unit tests."""
    return None
