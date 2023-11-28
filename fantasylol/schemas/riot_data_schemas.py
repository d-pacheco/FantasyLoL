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
    image: str= Field(
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
    league_id: int= Field(
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