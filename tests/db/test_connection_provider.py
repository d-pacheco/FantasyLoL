"""Test that DatabaseConnectionProvider is a pure connection pool (no DDL)."""

import os

from sqlalchemy import text

from src.db.database_connection_provider import DatabaseConnectionProvider

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/fantasy_lol_test",
)


def test_provider_does_not_import_models():
    """DatabaseConnectionProvider should have no dependency on Base/models."""
    import src.db.database_connection_provider as mod

    source = open(mod.__file__).read()
    assert "Base" not in source
    assert "create_all" not in source


def test_provider_yields_working_session():
    """Provider should yield a session that can execute a simple query."""
    provider = DatabaseConnectionProvider(database_url=TEST_DATABASE_URL)
    with provider.get_db() as session:
        result = session.execute(text("SELECT 1"))
        assert result.scalar() == 1
