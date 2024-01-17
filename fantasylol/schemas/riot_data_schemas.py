from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class League(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(
        default=None,
        description="The ID of the league",
        examples=["98767975604431411"]
    )
    slug: str = Field(
        default=None,
        description="The SLUG of the league",
        examples=["worlds"]
    )
    name: str = Field(
        default=None,
        description="The name of the league",
        examples=["Worlds"]
    )
    region: str = Field(
        default=None,
        description="The region of the league",
        examples=["INTERNATIONAL"]
    )
    image: str = Field(
        default=None,
        description="The image url of the league",
        examples=["http://static.lolesports.com/leagues/1592594612171_WorldsDarkBG.png"]
    )
    priority: int = Field(
        default=None,
        description="The priority of league in list ranking order",
        examples=[300]
    )


class TournamentStatus(str, Enum):
    COMPLETED = "completed"
    ACTIVE = "active"
    UPCOMING = "upcoming"


class Tournament(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(
        default=None,
        description="The ID of the tournament",
        examples=["110852926142971547"]
    )
    slug: str = Field(
        default=None,
        description="The SLUG of the tournament",
        examples=["worlds_2023"]
    )
    start_date: str = Field(
        default=None,
        description="The start date of the tournament",
        examples=["2023-10-09"]
    )
    end_date: str = Field(
        default=None,
        description="The end date of the tournament",
        examples=["2023-11-19"]
    )
    league_id: str = Field(
        default=None,
        description="The ID of the league the tournament is being held in",
        examples=["98767975604431411"]
    )


class Match(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(
        default=None,
        description="The ID of the match",
        examples=["110853020184706765"]
    )
    start_time: str = Field(
        default=None,
        description="The start time of the match",
        examples=["2023-11-19T08:00:00Z"]
    )
    block_name: str = Field(
        default=None,
        description="The block name of the match",
        examples=["Finals"]
    )
    league_slug: str = Field(
        default=None,
        description="The slug of the league the match is in",
        examples=["worlds"]
    )
    strategy_type: str = Field(
        default=None,
        description="The strategy type of the match",
        examples=["bestOf"]
    )
    strategy_count: int = Field(
        default=None,
        description="The number of games for the strategy type",
        examples=[5]
    )
    tournament_id: str = Field(
        default=None,
        description="The id of the tournament the match is taking place in",
        examples=["110852926142971547"]
    )
    team_1_name: str = Field(
        default=None,
        description="The name of the first team participating in the match",
        examples=["WeiboGaming FAW AUDI"]
    )
    team_2_name: str = Field(
        default=None,
        description="The name of the second team participating in the match",
        examples=["T1"]
    )


class GameState(str, Enum):
    COMPLETED = "completed"
    INPROGRESS = "inProgress"
    UNSTARTED = "unstarted"
    UNNEEDED = "unneeded"


class Game(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(
        default=None,
        description="The ID of the game",
        examples=["110853020184706766"]
    )
    state: GameState = Field(
        default=None,
        description="The state of the game",
        examples=["completed"]
    )
    number: int = Field(
        default=None,
        description="The game number within the strategy type and count",
        examples=[1]
    )
    match_id: str = Field(
        default=None,
        description="The ID of the match that the game is in",
        examples=["110853020184706765"]
    )
    has_game_data: bool = Field(
        default=True,
        description="If this game has player metadata and stats available",
        examples=[True]
    )


class GetGamesResponseSchema(BaseModel):
    id: str = Field()
    state: GameState = Field()


class ProfessionalTeam(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(
        default=None,
        description="The ID of the team",
        examples=["98767991853197861"]
    )
    slug: str = Field(
        default=None,
        description="The SLUG of the team",
        examples=["t1"]
    )
    name: str = Field(
        default=None,
        description="The name of the team",
        examples=["T1"]
    )
    code: str = Field(
        default=None,
        description="The code of the team",
        examples=["T1"]
    )
    image: str = Field(
        default=None,
        description="The image url of the team",
        examples=["http://static.lolesports.com/teams/1704375161752_T1_esports.png"]
    )
    alternative_image: str = Field(
        default=None,
        description="The alternative image url of the team",
        examples=["http://static.lolesports.com/teams/1704375161753_T1_esports.png"]
    )
    background_image: str = Field(
        default=None,
        description="The background image url of the team",
        examples=["http://static.lolesports.com/teams/1596305556675_T1T1.png"]
    )
    status: str = Field(
        default=None,
        description="The status of the team",
        examples=["active"]
    )
    home_league: str = Field(
        default=None,
        description="The home league name of the team",
        examples=["LCK"]
    )


class PlayerRole(str, Enum):
    TOP = "top"
    JUNGLE = "jungle"
    MID = "mid"
    BOTTOM = "bottom"
    SUPPORT = "support"
    NONE = "none"


class ProfessionalPlayer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(
        default=None,
        description="The esports id of the player given by RIOT",
        examples=["98767991747728851"]
    )
    summoner_name: str = Field(
        default=None,
        description="The summoner name of the player",
        examples=["Faker"]
    )
    image: str = Field(
        default=None,
        description="The url for the players image",
        examples=["http://static.lolesports.com/players/1686475867148_T1_Faker.png"]
    )
    role: str = Field(
        default=None,
        description="The role that the player plays",
        examples=["mid"]
    )
    team_id: str = Field(
        default=None,
        description="The id of the team that the player is on",
        examples=["98767991853197861"]
    )


class PlayerGameMetadata(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    game_id: str = Field(
        default=None,
        description="The id of the game this players metadata is for"
    )
    player_id: str = Field(
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
    model_config = ConfigDict(from_attributes=True)

    game_id: str = Field(
        default=None,
        description="The id of the game this players metadata is for"
    )
    participant_id: str = Field(
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
