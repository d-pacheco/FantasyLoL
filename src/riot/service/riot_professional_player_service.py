import logging

from sqlalchemy import or_

from src.common.schemas.search_parameters import PlayerSearchParameters
from src.common.schemas.riot_data_schemas import ProfessionalPlayer, ProPlayerID
from src.db.database_service import DatabaseService
from src.db.models import ProfessionalPlayerModel, ProfessionalTeamModel, LeagueModel
from src.common.exceptions import ProfessionalPlayerNotFoundException

logger = logging.getLogger("api.riot")


class RiotProfessionalPlayerService:
    def __init__(self, database_service: DatabaseService):
        self.db = database_service

    def get_players(self, search_parameters: PlayerSearchParameters) -> list[ProfessionalPlayer]:
        filters = []
        if search_parameters.summoner_name is not None:
            filters.append(
                ProfessionalPlayerModel.summoner_name.ilike(f"%{search_parameters.summoner_name}%")
            )
        if search_parameters.team_name is not None:
            term = f"%{search_parameters.team_name}%"
            filters.append(
                or_(
                    ProfessionalTeamModel.name.ilike(term),
                    ProfessionalTeamModel.code.ilike(term),
                )
            )
        if search_parameters.role is not None:
            filters.append(ProfessionalPlayerModel.role == search_parameters.role)
        if search_parameters.fantasy_available is not None:
            filters.append(LeagueModel.fantasy_available == search_parameters.fantasy_available)
        if search_parameters.active_only:
            filters.append(ProfessionalTeamModel.status == "active")

        professional_players = self.db.get_players(filters)
        return professional_players

    def get_player_by_id(self, professional_player_id: ProPlayerID) -> ProfessionalPlayer:
        professional_player = self.db.get_player_by_id(professional_player_id)
        if professional_player is None:
            raise ProfessionalPlayerNotFoundException()
        return professional_player
