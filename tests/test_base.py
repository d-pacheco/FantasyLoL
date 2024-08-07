import unittest
import logging
from sqlalchemy import MetaData

from src.db.database import engine
from src.db import models

RIOT_API_REQUESTER_CLOUDSCRAPER_PATH = \
    'src.riot.util.riot_api_requester.cloudscraper.create_scraper'

BASE_CRUD_PATH = 'src.db.crud'


class FantasyLolTestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if cls is not FantasyLolTestBase and cls.setUp is not FantasyLolTestBase.setUp:
            orig_setUp = cls.setUp

            def setUpOverride(self, *args, **kwargs):
                FantasyLolTestBase.setUp(self)
                return orig_setUp(self, *args, **kwargs)
            cls.setUp = setUpOverride  # type: ignore

    def setUp(self):
        logging.disable()
        models.Base.metadata.create_all(bind=engine)

    def tearDown(self):
        metadata = MetaData()

        # Reflect the existing tables
        metadata.reflect(bind=engine)

        with engine.begin() as connection:
            for table in reversed(metadata.sorted_tables):
                # Use the Table object to issue a DELETE statement
                connection.execute(table.delete())
