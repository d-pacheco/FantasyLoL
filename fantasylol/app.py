from fastapi import FastAPI

from fantasylol.api import router as api_router
from fantasylol.db.database import engine
from fantasylol.db import models


app = FastAPI()
app.include_router(api_router)
models.Base.metadata.create_all(bind=engine)