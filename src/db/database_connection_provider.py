from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool

from src.common.singleton_meta import SingletonMeta
from src.db.models import Base
from src.db.views import create_player_game_view_query
from src.db.database_config import DatabaseConfig


class DatabaseConnectionProvider(metaclass=SingletonMeta):
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine = create_engine(
            url=self.config.database_url,
            poolclass=QueuePool,
            pool_size=config.pool_size,
            max_overflow=config.max_overflow,
            connect_args={"check_same_thread": False}
        )
        self.SessionLocal = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        )
        self._initialize_database()

    def _initialize_database(self):
        Base.metadata.create_all(bind=self.engine)
        with self.engine.connect() as connection:
            connection.execute(create_player_game_view_query)
            connection.commit()

    @contextmanager
    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
