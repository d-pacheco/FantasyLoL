import os
import json
import sys
from dotenv import load_dotenv


class Config:
    load_dotenv()

    DATABASE_URL: str = os.getenv(
        'DATABASE_URL',
        "sqlite:///./fantasy-league-of-legends.db"
    )

    USE_TEST_DB = 'tests' in sys.argv

    DEBUG_LOGGING: bool = os.getenv('DEBUG_LOGGING', False)

    LEAGUE_SERVICE_SCHEDULE = json.loads(
        os.getenv(
            'LEAGUE_SERVICE_SCHEDULE',
            '{"trigger": "cron", "hour": "10", "minute": "00"}'
        )
    )

    TOURNAMENT_SERVICE_SCHEDULE = json.loads(
        os.getenv(
            'TOURNAMENT_SERVICE_SCHEDULE',
            '{"trigger": "cron", "hour": "10", "minute": "05"}'
        )
    )
