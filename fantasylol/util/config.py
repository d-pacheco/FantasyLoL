import os
import json
from dotenv import load_dotenv

class Config:
    load_dotenv()

    DATABASE_URL: str = os.getenv(
        'DATABASE_URL', 
        "sqlite:///./fantasy-league-of-legendsss.db"
    )
            
    USE_TEST_DB = True if os.getenv('USE_TEST_DB') is None else \
            os.getenv('USE_TEST_DB').lower() == 'true'
    
    LEAGUE_SERVICE_SCHEDULE = json.loads(
        os.getenv(
            'LEAGUE_SERVICE_SCHEDULE', 
            '{"trigger": "cron", "hour": "10", "minute": "00"}'
        )
    )

    TOURNAMENT_SERVICE_SCHEDULE = json.loads(
        os.getenv(
            'LEAGUE_SERVICE_SCHEDULE', 
            '{"trigger": "cron", "hour": "10", "minute": "05"}'
        )
    )
