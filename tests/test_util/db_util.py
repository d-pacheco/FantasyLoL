from typing import List

from src.db.database import DatabaseConnection
from src.db import models
from src.common.schemas.fantasy_schemas import FantasyLeagueID


def get_all_league_memberships(
        league_id: FantasyLeagueID) -> List[models.FantasyLeagueMembershipModel]:
    with DatabaseConnection() as db:
        return db.query(models.FantasyLeagueMembershipModel) \
            .filter(models.FantasyLeagueMembershipModel.league_id == league_id).all()
