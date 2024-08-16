from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

from . import views, models
from src.common import Config

Path("./database/").mkdir(parents=True, exist_ok=True)
PRODUCTION_DATABASE_URL = Config.DATABASE_URL
TEST_DATABASE_URL = "sqlite:///./fantasy-league-of-legends-test.db"

SQLALCHEMY_DATABASE_URL = TEST_DATABASE_URL if Config.TESTS_RUNNING else PRODUCTION_DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

models.Base.metadata.create_all(bind=engine)

with engine.connect() as connection:
    connection.execute(views.create_player_game_view_query)
    connection.commit()

views.Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class DatabaseConnection:
    def __enter__(self):
        self.db = SessionLocal()
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db:
            self.db.close()
