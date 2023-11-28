import unittest
from sqlalchemy import inspect

from fantasylol.db.database import engine
from fantasylol.db import models


RIOT_API_REQUESTER_CLOUDSCRAPER_PATH = 'fantasylol.util.riot_api_requester.cloudscraper.create_scraper'

class FantasyLolTestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if cls is not FantasyLolTestBase and cls.setUp is not FantasyLolTestBase.setUp:
            orig_setUp = cls.setUp

            def setUpOverride(self, *args, **kwargs):
                FantasyLolTestBase.setUp(self)
                return orig_setUp(self, *args, **kwargs)
            cls.setUp = setUpOverride

    def setUp(self):
        models.Base.metadata.create_all(bind=engine)

    def tearDown(self):
        inspector = inspect(engine)
        table_names = inspector.get_table_names()

        with engine.begin() as connection:
            for table_name in table_names:
                # Replace "table_name" with the actual table name
                connection.execute(f'DELETE FROM {table_name}')
