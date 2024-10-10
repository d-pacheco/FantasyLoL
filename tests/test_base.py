import unittest
import logging
import os
from sqlalchemy import MetaData

# JWT Auth Config Settings:
os.environ['AUTH_SECRET'] = "1234567890"
os.environ['AUTH_ALGORITHM'] = "HS256"

from tests.test_util.db_util import TestDatabaseService
from src.db import models  # type: ignore
from src.db.database_connection_provider import DatabaseConnectionProvider
from src.db.database_service import DatabaseService


# Email Verification Config Settings:
os.environ['VERIFICATION_DOMAIN_URL'] = "http://localhost"
os.environ['VERIFICATION_SENDER_EMAIL'] = "testEmail@gmail.com"
os.environ['VERIFICATION_SENDER_PASSWORD'] = "testpassword"
os.environ['VERIFICATION_SMTP_HOST'] = "smtp.gmail.com"
os.environ['VERIFICATION_SMTP_PORT'] = "465"


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
        cls.db_provider = DatabaseConnectionProvider(database_url=TEST_DATABASE_URL)
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
