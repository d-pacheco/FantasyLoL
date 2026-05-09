import logging

from src.common.schemas.search_parameters import PlayerSearchParameters
from src.common.schemas.riot_data_schemas import ProfessionalPlayer, ProPlayerID
from src.db.database_service import DatabaseService
from src.db.models import ProfessionalPlayerModel
from src.common.exceptions import ProfessionalPlayerNotFoundException

logger = logging.getLogger("api.riot")


class RiotProfessionalPlayerService:
    def __init__(self, database_service: DatabaseService):
        self.db = database_service

    def get_players(self, search_parameters: PlayerSearchParameters) -> list[ProfessionalPlayer]:
        filters = []
        join_league = False
        if search_parameters.summoner_name is not None:
            filters.append(
                ProfessionalPlayerModel.summoner_name.ilike(f"%{search_parameters.summoner_name}%")
            )
        if search_parameters.team_name is not None:
            from src.db.models import ProfessionalTeamModel

            filters.append(ProfessionalTeamModel.name.ilike(f"%{search_parameters.team_name}%"))
        if search_parameters.role is not None:
            filters.append(ProfessionalPlayerModel.role == search_parameters.role)
        if search_parameters.fantasy_available is not None:
            from src.db.models import LeagueModel

            join_league = True
            filters.append(LeagueModel.fantasy_available == search_parameters.fantasy_available)
        if search_parameters.active_only:
            from src.db.models import ProfessionalTeamModel as TeamModel

            filters.append(TeamModel.status == "active")

        professional_players = self.db.get_players(filters, join_league=join_league)
        return professional_players

    def get_player_by_id(self, professional_player_id: ProPlayerID) -> ProfessionalPlayer:
        professional_player = self.db.get_player_by_id(professional_player_id)
        if professional_player is None:
            raise ProfessionalPlayerNotFoundException()
        return professional_player
