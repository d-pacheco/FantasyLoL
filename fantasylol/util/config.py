import os
import json
import sys
from dotenv import load_dotenv

class Config:
    load_dotenv()

    DATABASE_URL: str = os.getenv(
        'DATABASE_URL', 
        "sqlite:///./fantasy-league-of-legendsss.db"
    )
            
    USE_TEST_DB = 'tests' in sys.argv
    
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
