from pydantic import BaseModel, Field

from fantasylol.schemas.game_state import GameState


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
    tournament_id: int = Field(
        default=None,
        description="The ID of the tournament that the game is in"
    )
    team_1_id: int = Field(
        default=None,
        description="The ID of team 1 in the game"
    )
    team_2_id: int = Field(
        default=None,
        description="The ID of team 2 in the game"
    )

    class ExampleResponse:
        example = {
            "id": 123456789,
            "state": "inProgress",
            "number": 2,
            "tournament_id": 777777,
            "team_1_id": 333,
            "team_2_id": 222,
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
    id: str = Field(
        default=None,
        description="The id of the player and team entry in the fantasy system"
    )
    esports_id: int = Field(
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
            "id": "b8c4eaf1-a16a-4db3-913b-c4a359595778",
            "esports_id": 123456789,
            "summoner_name": "summonerName",
            "image": "http://player-image.png",
            "role": "jungle",
            "team_id": 987654321
        }
