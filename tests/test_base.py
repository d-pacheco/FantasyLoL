import unittest
import logging
from sqlalchemy import MetaData

from tests.test_util.db_util import TestDatabaseService

from src.db import models
from src.db.database_config import DatabaseConfig
from src.db.database_connection_provider import DatabaseConnectionProvider
from src.db.database_service import DatabaseService

RIOT_API_REQUESTER_CLOUDSCRAPER_PATH = \
    'src.riot.util.riot_api_requester.cloudscraper.create_scraper'

BASE_CRUD_PATH = 'src.db.crud'

TEST_DATABASE_URL = 'sqlite:///:memory:'


class TestBase(unittest.TestCase):
    db_provider: DatabaseConnectionProvider
    db: DatabaseService
    test_db: TestDatabaseService

    @classmethod
    def setUpClass(cls) -> None:
        cls.db_provider = DatabaseConnectionProvider(
            DatabaseConfig(database_url=TEST_DATABASE_URL, pool_size=1, max_overflow=0)
        )
        cls.db = DatabaseService(cls.db_provider)
        cls.test_db = TestDatabaseService(cls.db_provider)

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
        metadata.reflect(bind=engine)

        with engine.begin() as connection:
            for table in reversed(metadata.sorted_tables):
                # Use the Table object to issue a DELETE statement
                connection.execute(table.delete())
