from fastapi import FastAPI
from fastapi_pagination import add_pagination
from fastapi_pagination.utils import disable_installed_extensions_check

from fantasylol.util.state_transition import StateTransitionHandler
from fantasylol.endpoints import router as api_router
from fantasylol.db.database import engine
from fantasylol.db import models


app = FastAPI()
add_pagination(app)
disable_installed_extensions_check()
app.include_router(api_router)
models.Base.metadata.create_all(bind=engine)
StateTransitionHandler.configure_listeners()
