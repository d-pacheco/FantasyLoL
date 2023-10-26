import datetime
import random

from db.database import DatabaseConnection
from db.models import Tournament

class TournamentTestUtil:
    def create_active_tournament():
        return create_tournament_with_modified_dates(-3, 3)

    def create_completed_tournament():
        return create_tournament_with_modified_dates(-6, -3)

    def create_upcoming_tournament():
        return create_tournament_with_modified_dates(3, 6)

def create_tournament_with_modified_dates(start_date_modifier: int, end_date_modifier: int):
    today = datetime.date.today()
    modified_start_date = today + datetime.timedelta(days=start_date_modifier)
    modified_end_date = today + datetime.timedelta(days=end_date_modifier)
    tournament_attrs = {
        "id": random.randint(100000, 999999),
        "slug": "mock-tournament-slug",
        "start_date": modified_start_date,
        "end_date": modified_end_date,
        "league_id": random.randint(100000, 999999)
    }
    tournament = Tournament(**tournament_attrs)
    with DatabaseConnection() as db:
        db.add(tournament)
        db.commit()
        db.refresh(tournament)
    return tournament