from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool

from src.db.models import Base
from src.db.views import create_player_game_view_query, create_match_view_query


class DatabaseConnectionProvider:
    def __init__(self, database_url: str):
        self.engine = create_engine(
            url=database_url,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
        )
        self.SessionLocal = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        )
        self._initialize_database()

    def _initialize_database(self):
        Base.metadata.create_all(bind=self.engine)
        with self.engine.connect() as connection:
            connection.execute(create_player_game_view_query)
            connection.execute(create_match_view_query)
            connection.commit()

    @contextmanager
    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
