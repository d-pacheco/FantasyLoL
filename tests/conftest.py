import os

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination
from fastapi_pagination.utils import disable_installed_extensions_check
from sqlalchemy import MetaData
from unittest.mock import MagicMock

# Set env vars before any app imports
os.environ.setdefault("AUTH_SECRET", "1234567890")
os.environ.setdefault("AUTH_ALGORITHM", "HS256")
os.environ.setdefault("REQUIRE_EMAIL_VERIFICATION", "True")
os.environ.setdefault("VERIFICATION_DOMAIN_URL", "http://localhost")
os.environ.setdefault("VERIFICATION_SENDER_EMAIL", "testEmail@gmail.com")
os.environ.setdefault("VERIFICATION_SENDER_PASSWORD", "testpassword")
os.environ.setdefault("VERIFICATION_SMTP_HOST", "smtp.gmail.com")
os.environ.setdefault("VERIFICATION_SMTP_PORT", "465")

from src.auth import JWTBearer  # noqa: E402
from src.db import models  # noqa: E402
from src.db.database_connection_provider import DatabaseConnectionProvider  # noqa: E402
from src.db.database_service import DatabaseService  # noqa: E402

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/fantasy_lol_test",
)


@pytest.fixture(scope="session")
def db_provider():
    provider = DatabaseConnectionProvider(database_url=TEST_DATABASE_URL)
    # Drop and recreate all tables so FK constraints are always current.
    # The view must be dropped first since it depends on underlying tables.
    from sqlalchemy import text

    with provider.engine.begin() as conn:
        conn.execute(text("DROP VIEW IF EXISTS player_game_view CASCADE"))
        conn.execute(text("DROP VIEW IF EXISTS match_view CASCADE"))
    models.Base.metadata.drop_all(bind=provider.engine)
    models.Base.metadata.create_all(bind=provider.engine)
    from src.db.views import create_player_game_view_query, create_match_view_query

    with provider.engine.connect() as conn:
        conn.execute(create_player_game_view_query)
        conn.execute(create_match_view_query)
        conn.commit()
    return provider


@pytest.fixture(scope="session")
def db(db_provider):
    return DatabaseService(db_provider)


@pytest.fixture(autouse=True)
def setup_and_teardown_tables(db_provider):
    """Create tables before each test and clean data after."""
    models.Base.metadata.create_all(bind=db_provider.engine)
    yield
    engine = db_provider.engine
    metadata = MetaData()
    metadata.reflect(bind=engine, views=False)
    with engine.begin() as connection:
        for table in reversed(metadata.sorted_tables):
            connection.execute(table.delete())


@pytest.fixture
def create_endpoint_client():
    """Factory fixture that creates a TestClient for an endpoint class with auth bypassed."""

    def _create(endpoint_class):
        mock_service = MagicMock()
        endpoint = endpoint_class(mock_service)
        app = FastAPI()
        app.include_router(endpoint.router, prefix="/api/v1")
        for route in app.routes:
            for dep in getattr(route, "dependencies", []):
                if isinstance(dep.dependency, JWTBearer):
                    app.dependency_overrides[dep.dependency] = lambda: {}
        disable_installed_extensions_check()
        add_pagination(app)
        return TestClient(app), mock_service

    return _create
