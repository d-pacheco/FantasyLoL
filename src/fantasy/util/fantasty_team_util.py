from ...common.schemas.fantasy_schemas import FantasyLeague

from ...db import crud

from ..exceptions.fantasy_draft_exception import FantasyDraftException


class FantasyTeamUtil:
    @staticmethod
    def validate_player_from_available_league(fantasy_league: FantasyLeague, player_id: str):
        player_league_ids = crud.get_league_ids_for_player(player_id)
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
