from src.common.schemas.fantasy_schemas import FantasyLeague
from src.common.schemas.riot_data_schemas import ProPlayerID

from src.db.database_service import DatabaseService

from src.fantasy.exceptions import FantasyDraftException


class FantasyTeamUtil:
    def __init__(self, database_service: DatabaseService):
        self.db = database_service

    def validate_player_from_available_league(
        self, fantasy_league: FantasyLeague, player_id: ProPlayerID
    ) -> None:
        player_league_ids = self.db.get_league_ids_for_player(player_id)
        in_allowed_league = False
        for available_league_id in fantasy_league.available_leagues:
            if available_league_id in player_league_ids:
                in_allowed_league = True
                break
        if not in_allowed_league:
            raise FantasyDraftException(
                f"Player not in available league: Player with ID {player_id} is not from "
                f"one of the available leagues {fantasy_league.available_leagues}, for the "
                f"fantasy league with ID {fantasy_league.id}"
            )
