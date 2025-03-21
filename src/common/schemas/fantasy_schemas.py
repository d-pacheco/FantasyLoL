from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, field_validator, EmailStr
from typing import NewType

from .riot_data_schemas import RiotLeagueID, ProPlayerID, PlayerRole  # type: ignore

UserID = NewType('UserID', str)
FantasyLeagueID = NewType('FantasyLeagueID', str)


class UserAccountStatus(Enum):
    ACTIVE = "active"
    PENDING_VERIFICATION = "pendingVerification"
    DELETED = "deleted"


class UserCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    email: EmailStr
    password: str

    @field_validator('username')
    def validate_username(cls, username: str):
        if len(username) < 3:
            raise ValueError('Username must be at least 3 characters long')
        return username

    @field_validator('password')
    def validate_password(cls, password: str):
        if len(password) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return password


class UserLogin(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    password: str


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UserID
    username: str
    email: EmailStr
    password: bytes
    permissions: str | None = None
    account_status: UserAccountStatus = UserAccountStatus.ACTIVE
    verified: bool = False
    verification_token: str | None = None

    def set_permissions(self, permissions_list):
        self.permissions = ','.join(permissions_list)

    def get_permissions(self):
        return self.permissions.split(',') if self.permissions else []


class EmailRequest(BaseModel):
    email: EmailStr


class FantasyLeagueScoringSettings(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    fantasy_league_id: FantasyLeagueID | None = Field(
        description="The id of the fantasy league. This field is ignored in update requests",
        examples=['aaaaaaaa-1111-bbbb-2222-cccccccccccc'],
        default=None
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
    available_leagues: list[RiotLeagueID] = Field(
        default=[],
        description="The IDs for the riot leagues available for drafting players from",
        examples=[["98767991310872058"]]
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

    id: FantasyLeagueID
    owner_id: UserID
    status: FantasyLeagueStatus
    current_week: int | None = None
    current_draft_position: int | None = None


class FantasyLeagueMembershipStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    REVOKED = "revoked"


class FantasyLeagueMembership(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    league_id: FantasyLeagueID
    user_id: UserID
    status: FantasyLeagueMembershipStatus


class UsersFantasyLeagues(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pending: list[FantasyLeague]
    accepted: list[FantasyLeague]


class FantasyLeagueDraftOrder(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    fantasy_league_id: FantasyLeagueID
    user_id: UserID
    position: int


class FantasyLeagueDraftOrderResponse(BaseModel):
    user_id: UserID
    username: str
    position: int


class FantasyTeam(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    fantasy_league_id: FantasyLeagueID
    user_id: UserID
    week: int
    top_player_id: ProPlayerID | None = None
    jungle_player_id: ProPlayerID | None = None
    mid_player_id: ProPlayerID | None = None
    adc_player_id: ProPlayerID | None = None
    support_player_id: ProPlayerID | None = None

    def get_player_id_for_role(self, role: PlayerRole) -> ProPlayerID | None:
        if role == PlayerRole.TOP:
            return self.top_player_id
        if role == PlayerRole.JUNGLE:
            return self.jungle_player_id
        if role == PlayerRole.MID:
            return self.mid_player_id
        if role == PlayerRole.BOTTOM:
            return self.adc_player_id
        if role == PlayerRole.SUPPORT:
            return self.support_player_id
        else:
            return None

    def set_player_id_for_role(self, player_id: ProPlayerID | None, role: PlayerRole) -> None:
        if role == PlayerRole.TOP:
            self.top_player_id = player_id
        if role == PlayerRole.JUNGLE:
            self.jungle_player_id = player_id
        if role == PlayerRole.MID:
            self.mid_player_id = player_id
        if role == PlayerRole.BOTTOM:
            self.adc_player_id = player_id
        if role == PlayerRole.SUPPORT:
            self.support_player_id = player_id
