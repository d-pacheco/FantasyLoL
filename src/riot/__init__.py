from fastapi import FastAPI
from fastapi_pagination import add_pagination
from fastapi_pagination.utils import disable_installed_extensions_check

from .endpoints import router as api_router


app = FastAPI()
add_pagination(app)
disable_installed_extensions_check()
app.include_router(api_router)
# StateTransitionHandler.configure_listeners()
