from pydantic import BaseModel


class DatabaseConfig(BaseModel):
    database_url: str
    pool_size: int = 5
    max_overflow: int = 10
