import unittest
import logging
import os
from sqlalchemy import MetaData

# JWT Auth Config Settings:
os.environ["AUTH_SECRET"] = "1234567890"
os.environ["AUTH_ALGORITHM"] = "HS256"

# Email Verification Config Settings:
os.environ["VERIFICATION_DOMAIN_URL"] = "http://localhost"
os.environ["VERIFICATION_SENDER_EMAIL"] = "testEmail@gmail.com"
os.environ["VERIFICATION_SENDER_PASSWORD"] = "testpassword"
os.environ["VERIFICATION_SMTP_HOST"] = "smtp.gmail.com"
os.environ["VERIFICATION_SMTP_PORT"] = "465"

from tests.test_util.db_util import TestDatabaseService
from src.db import models  # type: ignore
from src.db.database_connection_provider import DatabaseConnectionProvider
from src.db.database_service import DatabaseService

RIOT_API_REQUESTER_CLOUDSCRAPER_PATH = (
    "src.riot_scraper.riot_api_requester.cloudscraper.create_scraper"
)

BASE_CRUD_PATH = "src.db.crud"

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/fantasy_lol_test"
)


class TestBase(unittest.TestCase):
    db_provider: DatabaseConnectionProvider
    db: DatabaseService
    test_db: TestDatabaseService

    @classmethod
    def setUpClass(cls) -> None:
        cls.db_provider = DatabaseConnectionProvider(database_url=TEST_DATABASE_URL)
        cls.db = DatabaseService(cls.db_provider)
        cls.test_db = TestDatabaseService(cls.db_provider)

        # Drop and recreate all tables so FK constraints are always current.
        from sqlalchemy import text
        from src.db.views import create_player_game_view_query, create_match_view_query

        with cls.db_provider.engine.begin() as conn:
            conn.execute(text("DROP VIEW IF EXISTS player_game_view CASCADE"))
            conn.execute(text("DROP VIEW IF EXISTS match_view CASCADE"))
        models.Base.metadata.drop_all(bind=cls.db_provider.engine)
        models.Base.metadata.create_all(bind=cls.db_provider.engine)
        with cls.db_provider.engine.connect() as conn:
            conn.execute(create_player_game_view_query)
            conn.execute(create_match_view_query)
            conn.commit()

        if cls is not TestBase and cls.setUp is not TestBase.setUp:
            orig_setUp = cls.setUp

            def setUpOverride(self, *args, **kwargs):
                TestBase.setUp(self)
                return orig_setUp(self, *args, **kwargs)

            cls.setUp = setUpOverride  # type: ignore

    def setUp(self):
        logging.disable()
        models.Base.metadata.create_all(bind=self.db_provider.engine)

    def tearDown(self):
        engine = self.db_provider.engine
        metadata = MetaData()
        metadata.reflect(bind=engine, views=False)

        with engine.begin() as connection:
            for table in reversed(metadata.sorted_tables):
                connection.execute(table.delete())
