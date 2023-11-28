from pydantic import BaseModel, Field

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
        description="The ID of the tournament",
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


class GameSchema(BaseModel):
    id: int = Field(
        default=None, 
        description="The ID of the game",
    )
    start_time: str = Field(
        default=None, 
        description="The start time of the game"
    )
    block_name: str = Field(
        default=None, 
        description="The block name for the game"
    )
    strategy_type: str = Field(
        default=None, 
        description="The strategy type for the game"
    )
    strategy_count: int = Field(
        default=None, 
        description="The strategy count for the game"
    )
    state: str = Field(
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
            "start_time": "2023-08-07T05:00:00Z",
            "block_name": "Playoffs - Round 1",
            "strategy_type": "bestOf",
            "strategy_count": 5,
            "state": "inProgress",
            "number": 2,
            "tournament_id": 777777,
            "team_1_id": 333,
            "team_2_id": 222,
        }