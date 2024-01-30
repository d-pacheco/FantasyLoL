import uuid

from fantasylol.db import crud
from fantasylol.schemas.fantasy_schemas import FantasyLeague, FantasyLeagueCreate


class FantasyLeagueService:
    def create_fantasy_league(
            self, owner_id: str, league_create: FantasyLeagueCreate) -> FantasyLeague:
        fantasy_league_id = self.generate_new_valid_id()
        new_fantasy_league = FantasyLeague(
            id=fantasy_league_id,
            owner_id=owner_id,
            name=league_create.name
        )
        crud.create_fantasy_league(new_fantasy_league)
        return new_fantasy_league

    @staticmethod
    def generate_new_valid_id() -> str:
        while True:
            new_id = str(uuid.uuid4())
            if not crud.get_fantasy_league_by_id(new_id):
                break
        return new_id
