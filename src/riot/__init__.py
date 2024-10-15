from fastapi import FastAPI
from fastapi_pagination import add_pagination
from fastapi_pagination.utils import disable_installed_extensions_check


app = FastAPI()
add_pagination(app)
disable_installed_extensions_check()
