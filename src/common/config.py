import os
import json
import sys
from dotenv import load_dotenv
from typing import get_type_hints

from .exceptions import AppConfigException

load_dotenv()


class AppConfig:
    # Configure config default values
    DATABASE_URL: str = "sqlite:///./fantasy-league-of-legends.db"
    DEBUG_LOGGING: bool = False
    TESTS_RUNNING = 'test*.py' in sys.argv

    # Auth
    AUTH_SECRET: str
    AUTH_ALGORITHM: str

    # Api Requester:
    RIOT_API_KEY: str = "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"  # This is a public key
    ESPORTS_API_URL: str = "https://esports-api.lolesports.com/persisted/gw"
    ESPORTS_FEED_URL: str = "https://feed.lolesports.com/livestats/v1"

    # Job schedules:
    LEAGUE_SERVICE_SCHEDULE: dict = \
        '{"trigger": "cron", "hour": "10", "minute": "00"}'  # type: ignore
    TOURNAMENT_SERVICE_SCHEDULE: dict = \
        '{"trigger": "cron", "hour": "10", "minute": "05"}'  # type: ignore
    TEAM_SERVICE_SCHEDULE: dict = \
        '{"trigger": "cron", "hour": "10", "minute": "10"}'  # type: ignore
    PLAYER_SERVICE_SCHEDULE: dict = \
        '{"trigger": "cron", "hour": "10", "minute": "15"}'  # type: ignore
    MATCH_SERVICE_SCHEDULE: dict = \
        '{"trigger": "cron", "minute": "30"}'  # type: ignore
    GAME_SERVICE_SCHEDULE: dict = \
        '{"trigger": "cron", "minute": "45"}'  # type: ignore
    GAME_STATS_SERVICE_SCHEDULE: dict = \
        '{"trigger": "cron", "minute": "*/5"}'  # type: ignore

    def __init__(self, env):
        for field in self.__annotations__:
            if not field.isupper():
                continue

            default_value = getattr(self, field, None)
            if default_value is None and env.get(field) is None:
                raise AppConfigException(f"The {field} field is required")

            try:
                var_type = get_type_hints(AppConfig)[field]
                if var_type == dict:
                    value = json.loads(env.get(field, default_value))
                else:
                    value = var_type(env.get(field, default_value))

                self.__setattr__(field, value)
            except ValueError:
                raise AppConfigException(
                    'Unable to cast value of "{}" to type "{}" for "{}" field'.format(
                        env[field], var_type, field
                    )
                )

    def __repr__(self):
        return str(self.__dict__)


app_config = AppConfig(os.environ)
