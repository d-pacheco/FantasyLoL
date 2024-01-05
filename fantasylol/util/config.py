import os
import json
import sys
from dotenv import load_dotenv
from typing import get_type_hints, Union
from fantasylol.exceptions.AppConfigException import AppConfigException

load_dotenv()


def _parse_bool(val: Union[str, bool]) -> bool:  # pylint: disable=E1136
    return val if type(val) == bool else val.lower() in ['true', 'yes', '1']


class AppConfig:
    # Configure config default values
    DATABASE_URL: str = "sqlite:///./fantasy-league-of-legends.db"
    DEBUG_LOGGING: bool = False
    LEAGUE_SERVICE_SCHEDULE: dict = '{"trigger": "cron", "hour": "10", "minute": "00"}'
    TOURNAMENT_SERVICE_SCHEDULE: dict = '{"trigger": "cron", "hour": "10", "minute": "05"}'
    USE_TEST_DB = 'tests' in sys.argv

    def __init__(self, env):
        for field in self.__annotations__:
            if not field.isupper():
                continue

            default_value = getattr(self, field, None)
            if default_value is None and env.get(field) is None:
                raise AppConfigException(f"The {field} field is required")

            try:
                var_type = get_type_hints(AppConfig)[field]
                if var_type == bool:
                    value = _parse_bool(env.get(field, default_value))
                elif var_type == dict:
                    value = json.loads(env.get(field, default_value))
                else:
                    value = var_type(env.get(field, default_value))

                self.__setattr__(field, value)
            except ValueError:
                raise AppConfigException('Unable to cast value of "{}" to type "{}" for "{}" field'.format(
                    env[field],
                    var_type,
                    field
                )
                )

    def __repr__(self):
        return str(self.__dict__)


Config = AppConfig(os.environ)
