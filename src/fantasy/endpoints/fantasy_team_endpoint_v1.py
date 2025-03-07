from classy_fastapi import Routable, get, put
from fastapi import Depends

from src.auth import JWTBearer, Permissions
from src.common.schemas.fantasy_schemas import FantasyTeam, FantasyLeagueID, UserID
from src.common.schemas.riot_data_schemas import ProPlayerID
from src.fantasy.service import FantasyTeamService


class FantasyTeamEndpoint(Routable):
    def __init__(self, fantasy_team_service: FantasyTeamService):
        super().__init__()
        self.__fantasy_team_service = fantasy_team_service

    @get(
        path="/teams/{fantasy_league_id}",
        description="Get all of the callers teams by week for a Fantasy League.",
        tags=["Fantasy Teams"],
        dependencies=[Depends(JWTBearer([Permissions.FANTASY_READ]))],
        response_model=list[FantasyTeam]
    )
    def get_fantasy_team_weeks_for_league(
            self,
            fantasy_league_id: FantasyLeagueID,
            decoded_token: dict = Depends(JWTBearer())
    ) -> list[FantasyTeam]:
        user_id = UserID(decoded_token.get("user_id"))  # type: ignore
        return self.__fantasy_team_service.get_all_fantasy_team_weeks(fantasy_league_id, user_id)

    @put(
        path="/teams/{fantasy_league_id}/pickup/{player_id}",
        description="Pickup a player for the current week within a Fantasy League.",
        tags=["Fantasy Teams"],
        dependencies=[Depends(JWTBearer([Permissions.FANTASY_WRITE]))],
        response_model=FantasyTeam
    )
    def pickup_player(
            self,
            fantasy_league_id: FantasyLeagueID,
            player_id: ProPlayerID,
            decoded_token: dict = Depends(JWTBearer())
    ) -> FantasyTeam:
        user_id = UserID(decoded_token.get("user_id"))  # type: ignore
        return self.__fantasy_team_service.pickup_player(fantasy_league_id, user_id, player_id)

    @put(
        path="/teams/{fantasy_league_id}/drop/{player_id}",
        description="Drop a player for the current week within a Fantasy League.",
        tags=["Fantasy Teams"],
        dependencies=[Depends(JWTBearer([Permissions.FANTASY_WRITE]))],
        response_model=FantasyTeam
    )
    def drop_player(
            self,
            fantasy_league_id: FantasyLeagueID,
            player_id: ProPlayerID,
            decoded_token: dict = Depends(JWTBearer())
    ) -> FantasyTeam:
        user_id = UserID(decoded_token.get("user_id"))  # type: ignore
        return self.__fantasy_team_service.drop_player(fantasy_league_id, user_id, player_id)

    @put(
        path="/teams/{fantasy_league_id}/swap/{player_to_drop_id}/{player_to_pickup_id}",
        description="Swap a player for another player in the current week within a Fantasy League.",
        tags=["Fantasy Teams"],
        dependencies=[Depends(JWTBearer([Permissions.FANTASY_WRITE]))],
        response_model=FantasyTeam
    )
    def swap_players(
            self,
            fantasy_league_id: FantasyLeagueID,
            player_to_drop_id: ProPlayerID,
            player_to_pickup_id: ProPlayerID,
            decoded_token: dict = Depends(JWTBearer())
    ) -> FantasyTeam:
        user_id = UserID(decoded_token.get("user_id"))  # type: ignore
        return self.__fantasy_team_service.swap_players(
            fantasy_league_id,
            user_id,
            player_to_drop_id,
            player_to_pickup_id
        )
