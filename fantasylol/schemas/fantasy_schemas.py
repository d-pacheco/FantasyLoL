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
