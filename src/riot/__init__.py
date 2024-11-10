from fastapi import FastAPI
from fastapi_pagination import add_pagination
from fastapi_pagination.utils import disable_installed_extensions_check


app = FastAPI(
    title="MythicForge Riot Data API",
    version="0.1.0",
    description="""
        Fetch data related to Professional League of Legends.
        To authorize with these endpoints you  will need to signup and login with an account for
        MythicForge Fantasy API. Once you have logged in, use the authorization token to
        authorize with the riot data API endpoints.
        The signup and login can be found here: fantasy.nightlenlab.com/docs
        """,
)
add_pagination(app)
disable_installed_extensions_check()
