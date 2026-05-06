"""Test that Alembic migrations produce a correct, usable schema."""

import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from alembic.config import Config
from alembic import command

from src.db.models import LeagueModel

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/fantasy_lol_test",
)

MIGRATION_TEST_DB = TEST_DATABASE_URL.rsplit("/", 1)[0] + "/fantasy_lol_migration_test"


@pytest.fixture
def migration_db():
    """Create a fresh database, run migrations, yield engine, then drop it."""
    root_engine = create_engine(
        TEST_DATABASE_URL.rsplit("/", 1)[0] + "/postgres", isolation_level="AUTOCOMMIT"
    )
    with root_engine.connect() as conn:
        conn.execute(text("DROP DATABASE IF EXISTS fantasy_lol_migration_test"))
        conn.execute(text("CREATE DATABASE fantasy_lol_migration_test"))
    root_engine.dispose()

    os.environ["DATABASE_URL"] = MIGRATION_TEST_DB
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", MIGRATION_TEST_DB)
    command.upgrade(alembic_cfg, "head")

    engine = create_engine(MIGRATION_TEST_DB)
    yield engine
    engine.dispose()

    root_engine = create_engine(
        TEST_DATABASE_URL.rsplit("/", 1)[0] + "/postgres", isolation_level="AUTOCOMMIT"
    )
    with root_engine.connect() as conn:
        conn.execute(text("DROP DATABASE IF EXISTS fantasy_lol_migration_test"))
    root_engine.dispose()


def test_migration_creates_tables(migration_db):
    """After running migrations, we can insert and query a league."""
    with Session(migration_db) as session:
        league = LeagueModel(
            id="test-league-1",
            slug="test",
            name="Test League",
            region="NA",
            image="http://example.com/img.png",
            priority=1,
            fantasy_available=False,
        )
        session.add(league)
        session.commit()

        result = session.query(LeagueModel).filter_by(id="test-league-1").first()
        assert result is not None
        assert result.name == "Test League"


def test_migration_creates_views(migration_db):
    """After running migrations, the views exist."""
    with Session(migration_db) as session:
        # Views should exist and be queryable (even if empty)
        result = session.execute(text("SELECT * FROM player_game_view LIMIT 1"))
        assert result.keys() is not None
        result = session.execute(text("SELECT * FROM match_view LIMIT 1"))
        assert result.keys() is not None
        result = session.execute(text("SELECT * FROM game_view LIMIT 1"))
        assert result.keys() is not None
