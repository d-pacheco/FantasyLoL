from typing import List

from ...common.schemas.fantasy_schemas import FantasyLeagueStatus

from ...db import crud
from ...db.models import FantasyLeagueModel

from ..exceptions.fantasy_league_not_found_exception import FantasyLeagueNotFoundException
from ..exceptions.fantasy_league_invalid_required_state_exception import \
    FantasyLeagueInvalidRequiredStateException


class FantasyLeagueUtil:
    @staticmethod
    def validate_league(
            fantasy_league_id: str,
            required_states: List[FantasyLeagueStatus] = None) -> FantasyLeagueModel:
        fantasy_league_model = crud.get_fantasy_league_by_id(fantasy_league_id)
        if fantasy_league_model is None:
            raise FantasyLeagueNotFoundException()

        if required_states is None:
            return fantasy_league_model

        if fantasy_league_model.status not in required_states:
            raise FantasyLeagueInvalidRequiredStateException(
                fantasy_league_id, fantasy_league_model.status, required_states
            )
        return fantasy_league_model
