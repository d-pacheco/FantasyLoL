from fastapi import FastAPI
from fastapi_pagination import add_pagination
from fastapi_pagination.utils import disable_installed_extensions_check


app = FastAPI(
    title="MythicForge Fantasy API",
    version="0.1.0",
    description="""
        Create and manage Fantasy League of Legends leagues and teams.
        Query Professional League of Legends data here: riot.nightlenlab.com/docs
        """,
)
add_pagination(app)
disable_installed_extensions_check()
