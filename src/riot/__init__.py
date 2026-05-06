from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from fastapi_pagination.utils import disable_installed_extensions_check

from src.common.config import app_config


# Kept for backward compatibility with tests that import `from src.riot import app`
app = FastAPI(
    title="MythicForge Riot Data API (deprecated - use src.app)",
    version="0.1.0",
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
