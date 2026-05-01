from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from fastapi_pagination.utils import disable_installed_extensions_check

from src.common.config import app_config


app = FastAPI(
    title="MythicForge Fantasy API",
    version="0.1.0",
    description="""
        Create and manage Fantasy League of Legends leagues and teams.
        Query Professional League of Legends data here: riot.nightlenlab.com/docs
        """,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
add_pagination(app)
disable_installed_extensions_check()
