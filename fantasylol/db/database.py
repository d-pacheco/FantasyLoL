from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from fantasylol.util.config import Config

PRODUCTION_DATABASE_URL = Config.DATABASE_URL
TEST_DATABASE_URL = "sqlite:///./fantasy-league-of-legends-test.db"

SQLALCHEMY_DATABASE_URL = TEST_DATABASE_URL if Config.USE_TEST_DB else PRODUCTION_DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class DatabaseConnection:
    def __enter__(self):
        self.db = SessionLocal()
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db:
            self.db.close()