from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool


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

    @contextmanager
    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
