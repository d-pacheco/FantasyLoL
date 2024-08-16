from typing import List

from src.db.database_connection_provider import DatabaseConnectionProvider
from src.db import models
from src.common.schemas.fantasy_schemas import FantasyLeagueID


class TestDatabaseService:
    def __init__(self, connection_provider: DatabaseConnectionProvider):
        self.connection_provider = connection_provider

    def get_all_league_memberships(
            self,
            league_id: FantasyLeagueID
    ) -> List[models.FantasyLeagueMembershipModel]:
        with self.connection_provider.get_db() as db:
            return db.query(models.FantasyLeagueMembershipModel) \
                .filter(models.FantasyLeagueMembershipModel.league_id == league_id).all()
