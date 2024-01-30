import uuid

from fantasylol.db import crud
from fantasylol.exceptions.fantasy_league_not_found_exception import FantasyLeagueNotFoundException
from fantasylol.exceptions.forbidden_exception import ForbiddenException
from fantasylol.schemas.fantasy_schemas import FantasyLeague, FantasyLeagueSettings


class FantasyLeagueService:
    def create_fantasy_league(
            self, owner_id: str, league_settings: FantasyLeagueSettings) -> FantasyLeague:
        fantasy_league_id = self.generate_new_valid_id()
        new_fantasy_league = FantasyLeague(
            id=fantasy_league_id,
            owner_id=owner_id,
            name=league_settings.name,
            number_of_teams=league_settings.number_of_teams
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

    @staticmethod
    def get_fantasy_league_settings(owner_id: str, league_id: str) -> FantasyLeagueSettings:
        fantasy_league_model = crud.get_fantasy_league_by_id(league_id)
        if fantasy_league_model is None:
            raise FantasyLeagueNotFoundException()
        if fantasy_league_model.owner_id != owner_id:
            raise ForbiddenException()

        league_settings = FantasyLeagueSettings(
            name=fantasy_league_model.name,
            number_of_teams=fantasy_league_model.number_of_teams
        )
        return league_settings
