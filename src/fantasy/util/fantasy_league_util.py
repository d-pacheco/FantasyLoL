from typing import List

from ...common.exceptions.league_not_found_exception import LeagueNotFoundException
from ...common.schemas.fantasy_schemas import FantasyLeagueStatus, FantasyLeague

from ...db import crud

from ..exceptions.fantasy_league_not_found_exception import FantasyLeagueNotFoundException
from ..exceptions.fantasy_league_invalid_required_state_exception import \
    FantasyLeagueInvalidRequiredStateException
from ..exceptions.fantasy_unavailable_exception import FantasyUnavailableException


class FantasyLeagueUtil:
    @staticmethod
    def validate_league(
            fantasy_league_id: str,
            required_states: List[FantasyLeagueStatus] = None) -> FantasyLeague:
        fantasy_league_model = crud.get_fantasy_league_by_id(fantasy_league_id)
        if fantasy_league_model is None:
            raise FantasyLeagueNotFoundException()

        if (required_states is not None) and (fantasy_league_model.status not in required_states):
            raise FantasyLeagueInvalidRequiredStateException(
                fantasy_league_id, fantasy_league_model.status, required_states
            )
        fantasy_league = FantasyLeague.model_validate(fantasy_league_model)
        return fantasy_league

    @staticmethod
    def validate_available_leagues(selected_league_ids: List[str]):
        riot_leagues = crud.get_leagues()
        league_dict = {league.id: league for league in riot_leagues}

        for league_id in selected_league_ids:
            if league_id not in league_dict:
                raise LeagueNotFoundException(f"Riot league with ID {league_id} not found")
            if not league_dict[league_id].fantasy_available:
                raise FantasyUnavailableException(
                    f"Riot league with ID {league_id} not available to be used in Fantasy Leagues"
                )

    @staticmethod
    def update_fantasy_leagues_current_draft_position(fantasy_league: FantasyLeague):
        if fantasy_league.current_draft_position + 1 <= fantasy_league.number_of_teams:
            new_draft_position = fantasy_league.current_draft_position + 1
        else:
            new_draft_position = 1
        crud.update_fantasy_league_current_draft_position(fantasy_league.id, new_draft_position)
