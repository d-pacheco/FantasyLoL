from pydantic import BaseModel, Field

from fantasylol.schemas.game_state import GameState
from fantasylol.schemas.player_role import PlayerRole


class LeagueSchema(BaseModel):
    id: int = Field(
        default=None,
        description="The ID of the league",
    )
    slug: str = Field(
        default=None,
        description="The SLUG of the league"
    )
    name: str = Field(
        default=None,
        description="The name of the league"
    )
    region: str = Field(
        default=None,
        description="The region of the league"
    )
    image: str = Field(
        default=None,
        description="The image url of the league"
    )
    priority: int = Field(
        default=None,
        description="The priority of league in list ranking order"
    )

    class ExampleResponse:
        example = {
            "id": 98767975604431411,
            "slug": "worlds",
            "name": "Words",
            "region": "INTERNATIONAL",
            "image": "http://static.lolesports.com/leagues/1592594612171_WorldsDarkBG.png",
            "priority": 300
        }


class TournamentSchema(BaseModel):
    id: int = Field(
        default=None,
        description="The ID of the tournament"
    )
    slug: str = Field(
        default=None,
        description="The SLUG of the tournament"
    )
    start_date: str = Field(
        default=None,
        description="The start date of the tournament"
    )
    end_date: str = Field(
        default=None,
        description="The end date of the tournament"
    )
    league_id: int = Field(
        default=None,
        description="The ID of the league the tournament is being held in"
    )

    class ExampleResponse:
        example = {
            "id": 123456789,
            "slug": "example_slug",
            "start_date": "2023-01-01",
            "end_date": "2023-02-01",
            "league_id": 98767975604431411
        }


class MatchSchema(BaseModel):
    id: int = Field(
        default=None,
        description="The ID of the match"
    )
    start_time: str = Field(
        default=None,
        description="The start time of the match"
    )
    block_name: str = Field(
        default=None,
        description="The block name of the match"
    )
    league_name: str = Field(
        default=None,
        description="The name of the league the match is in"
    )
    strategy_type: str = Field(
        default=None,
        description="The strategy type of the match"
    )
    strategy_count: int = Field(
        default=None,
        description="The number of games for the strategy type"
    )
    tournament_id: int = Field(
        default=None,
        description="The id of the tournament the match is taking place in"
    )
    team_1_name: str = Field(
        default=None,
        description="The name of the first team participating in the match"
    )
    team_2_name: str = Field(
        default=None,
        description="The name of the second team participating in the match"
    )

    class ExampleResponse:
        example = {
            "id": 110853020184706765,
            "start_time": "2023-11-19T08:00:00Z",
            "block_name": "Finals",
            "league_name": "Worlds",
            "strategy_type": "bestOf",
            "strategy_count": 5,
            "tournament_id": 123456789,
            "team_1_name": "WeiboGaming FAW AUDI",
            "team_2_name": "T1"
        }


class GameSchema(BaseModel):
    id: int = Field(
        default=None,
        description="The ID of the game",
    )
    state: GameState = Field(
        default=None,
        description="The state of the game"
    )
    number: int = Field(
        default=None,
        description="The game number within the strategy type and count"
    )
    match_id: int = Field(
        default=None,
        description="The ID of the match that the game is in"
    )
    has_game_data: bool = Field(
        default=True,
        description="If this game has player metadata and stats available"
    )

    class ExampleResponse:
        example = {
            "id": 110413246204026236,
            "state": "completed",
            "number": 1,
            "match_id": 110413246204026235,
        }


class ProfessionalTeamSchema(BaseModel):
    id: int = Field(
        default=None,
        description="The ID of the team",
    )
    slug: str = Field(
        default=None,
        description="The SLUG of the team"
    )
    name: str = Field(
        default=None,
        description="The name of the team"
    )
    code: str = Field(
        default=None,
        description="The code of the team"
    )
    image: str = Field(
        default=None,
        description="The image url of the team"
    )
    alternative_image: str = Field(
        default=None,
        description="The alternatice image url of the team"
    )
    background_image: str = Field(
        default=None,
        description="The background image url of the team"
    )
    status: str = Field(
        default=None,
        description="The status of the team"
    )
    home_league: str = Field(
        default=None,
        description="The home league name of the team"
    )

    class ExampleResponse:
        example = {
            "id": 123456789,
            "slug": "team_name",
            "name": "Team Name",
            "code": "TEST1",
            "image": "http://team-image.png",
            "alternative_image": "http://team-alternative-image.png",
            "background_image": "http://team-background-image.png",
            "status": "active",
            "home_league": "Challengers"
        }


class ProfessionalPlayerSchema(BaseModel):
    id: int = Field(
        default=None,
        description="The esports id of the player given by RIOT"
    )
    summoner_name: str = Field(
        default=None,
        description="The summoner name of the player"
    )
    image: str = Field(
        default=None,
        description="The url for the players image"
    )
    role: str = Field(
        default=None,
        description="The role that the player plays"
    )
    team_id: int = Field(
        default=None,
        description="The id of the team that the player is on"
    )

    class ExampleResponse:
        example = {
            "id": 123456789,
            "summoner_name": "summonerName",
            "image": "http://player-image.png",
            "role": "jungle",
            "team_id": 987654321
        }


class PlayerGameMetadataSchema(BaseModel):
    game_id: int = Field(
        default=None,
        description="The id of the game this players metadata is for"
    )
    player_id: int = Field(
        default=None,
        description="The id of the player given by riot"
    )
    participant_id: int = Field(
        default=None,
        description="The participant id for the game given by riot"
    )
    champion_id: str = Field(
        default=None,
        description="The id of the champion the player played in the game"
    )
    role: PlayerRole = Field(
        default=None,
        description="The role the player played in the game"
    )


class PlayerGameStatsSchema(BaseModel):
    game_id: int = Field(
        default=None,
        description="The id of the game this players metadata is for"
    )
    participant_id: int = Field(
        default=None,
        description="The participant id for the game given by riot"
    )
    kills: int = Field(
        default=None,
        description="The number of kills the player got"
    )
    deaths: int = Field(
        default=None,
        description="The number of deaths for the player"
    )
    assists: int = Field(
        default=None,
        description="The number of assists for the players"
    )
    total_gold: int = Field(
        default=None,
        description="The total gold the player had"
    )
    creep_score: int = Field(
        default=None,
        description="The creep score the player had"
    )
    kill_participation: int = Field(
        default=None,
        description="The kill participation the player had"
    )
    champion_damage_share: int = Field(
        default=None,
        description="The damage percentage of the team the player did to champions"
    )
    wards_placed: int = Field(
        default=None,
        description="The number of wards the player placed"
    )
    wards_destroyed: int = Field(
        default=None,
        description="The number of enemy wards the player destroyed"
    )


class RiotSchedulePages(BaseModel):
    older: str = Field(default=None)
    newer: str = Field(default=None)
