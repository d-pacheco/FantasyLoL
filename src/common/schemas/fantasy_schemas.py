from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    password: str


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    email: str
    password: str


class FantasyLeagueScoringSettings(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    fantasy_league_id: str = Field(
        description="The id of the fantasy league",
        examples=['aaaaaaaa-1111-bbbb-2222-cccccccccccc']
    )
    kills: int = Field(
        default=2,
        description="The number of points kills are worth in a given fantasy league",
        examples=[2]
    )
    deaths: int = Field(
        default=-1,
        description="The number of points deaths are worth in a given fantasy league",
        examples=[-1]
    )
    assists: float = Field(
        default=0.5,
        description="The number of points assists are worth in a given fantasy league",
        examples=[0.5]
    )
    creep_score: float = Field(
        default=0.05,
        description="The number of points creeps score are worth in a given fantasy league",
        examples=[0.05]
    )
    wards_placed: float = Field(
        default=0.1,
        description="The number of points wards placed are worth in a given fantasy league",
        examples=[0.1]
    )
    wards_destroyed: float = Field(
        default=0.1,
        description="The number of points wards destroyed are worth in a given fantasy league",
        examples=[0.1]
    )
    kill_participation: int = Field(
        default=10,
        description="The number of points kill participation is worth in a given fantasy league",
        examples=[10]
    )
    damage_percentage: int = Field(
        default=5,
        description="The number of points damage percentage is worth in a given fantasy league",
        examples=[5]
    )


class FantasyLeagueSettings(BaseModel):
    name: str = Field(
        default=None,
        description="The name of the fantasy league",
        examples=["My Fantasy League"]
    )
    number_of_teams: int = Field(
        default=6,
        description="Number of teams in the fantasy league\n"
                    "Allowed values: 4, 6, 8, 10"
    )

    @field_validator('number_of_teams')
    @classmethod
    def valid_team_size(cls, value: str):
        valid_values = {4, 6, 8, 10}
        if value not in valid_values:
            raise ValueError("Invalid number of teams. Allowed values: 4, 6, 8, 10")
        return value


class FantasyLeagueStatus(str, Enum):
    PRE_DRAFT = "pre-draft"
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    DELETED = "deleted"


class FantasyLeague(FantasyLeagueSettings):
    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_id: str
    status: FantasyLeagueStatus


class FantasyLeagueMembershipStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    REVOKED = "revoked"


class FantasyLeagueMembership(BaseModel):
    league_id: str
    user_id: str
    status: FantasyLeagueMembershipStatus


class FantasyLeagueDraftOrder(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    fantasy_league_id: str
    user_id: str
    position: int


class FantasyLeagueDraftOrderResponse(BaseModel):
    user_id: str
    username: str
    position: int
