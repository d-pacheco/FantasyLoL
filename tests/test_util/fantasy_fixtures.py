import uuid
import bcrypt
from random import randint

from src.auth.permissions import Permissions
from src.common.schemas.fantasy_schemas import (
    FantasyLeague,
    FantasyLeagueScoringSettings,
    FantasyLeagueSettings,
    FantasyLeagueStatus,
    FantasyLeagueID,
    FantasyTeam,
    User, UserCreate, UserLogin, UserID
)
from src.common.schemas.riot_data_schemas import ProPlayerID


user_password = "WeakTestPw"
salt = bcrypt.gensalt()
user_hashed_password = bcrypt.hashpw(str.encode(user_password), salt)

user_create_fixture: UserCreate = UserCreate(
    username=UserID("MyUsername"),
    email="MyEmail@gmail.com",
    password=user_password
)

user_login_fixture: UserLogin = UserLogin(
    username=user_create_fixture.username,
    password=user_password
)

user_fixture: User = User(
    id=UserID(str(uuid.uuid4())),
    username=user_create_fixture.username,
    email=user_create_fixture.email,
    password=user_hashed_password,
    permissions=f"{Permissions.FANTASY_READ.value},{Permissions.FANTASY_WRITE.value},"
                f"{Permissions.RIOT_READ.value}"
)

user_2_fixture: User = User(
    id=UserID(str(uuid.uuid4())),
    username="user2",
    email="user2@email.com",
    password=user_hashed_password,
    permissions=f"{Permissions.FANTASY_READ.value},{Permissions.FANTASY_WRITE.value},"
                f"{Permissions.RIOT_READ.value}"
)

user_3_fixture: User = User(
    id=UserID(str(uuid.uuid4())),
    username="user3",
    email="user3@email.com",
    password=user_hashed_password,
    permissions=f"{Permissions.FANTASY_READ.value},{Permissions.FANTASY_WRITE.value},"
                f"{Permissions.RIOT_READ.value}"
)

user_4_fixture: User = User(
    id=UserID(str(uuid.uuid4())),
    username="user4",
    email="user4@email.com",
    password=user_hashed_password,
    permissions=f"{Permissions.FANTASY_READ.value},{Permissions.FANTASY_WRITE.value},"
                f"{Permissions.RIOT_READ.value}"
)

fantasy_league_settings_fixture: FantasyLeagueSettings = FantasyLeagueSettings(
    name="Fantasy League 1",
    number_of_teams=6,
    available_leagues=[]
)

fantasy_league_fixture: FantasyLeague = FantasyLeague(
    id=FantasyLeagueID(str(uuid.uuid4())),
    owner_id=user_fixture.id,
    status=FantasyLeagueStatus.PRE_DRAFT,
    name=fantasy_league_settings_fixture.name,
    number_of_teams=fantasy_league_settings_fixture.number_of_teams,
    available_leagues=fantasy_league_settings_fixture.available_leagues,
    current_week=None
)

fantasy_league_draft_fixture: FantasyLeague = FantasyLeague(
    id=FantasyLeagueID(str(uuid.uuid4())),
    owner_id=user_fixture.id,
    status=FantasyLeagueStatus.DRAFT,
    name=fantasy_league_settings_fixture.name,
    number_of_teams=fantasy_league_settings_fixture.number_of_teams,
    available_leagues=fantasy_league_settings_fixture.available_leagues,
    current_draft_position=1,
    current_week=0
)

fantasy_league_active_fixture: FantasyLeague = FantasyLeague(
    id=FantasyLeagueID(str(uuid.uuid4())),
    owner_id=user_fixture.id,
    status=FantasyLeagueStatus.ACTIVE,
    name=fantasy_league_settings_fixture.name,
    number_of_teams=fantasy_league_settings_fixture.number_of_teams,
    available_leagues=fantasy_league_settings_fixture.available_leagues,
    current_week=1
)

fantasy_league_scoring_settings_fixture: FantasyLeagueScoringSettings = \
    FantasyLeagueScoringSettings(
        fantasy_league_id=fantasy_league_fixture.id,
        kills=4,
        deaths=2,
        assists=1,
        creep_score=0.8,
        wards_placed=0.2,
        wards_destroyed=0.2,
        kill_participation=15,
        damage_percentage=8
    )

fantasy_team_full: FantasyTeam = FantasyTeam(
    fantasy_league_id=fantasy_league_active_fixture.id,
    user_id=user_fixture.id,
    week=1,
    top_player_id=ProPlayerID(str((randint(10000, 99999)))),
    jungle_player_id=ProPlayerID(str((randint(10000, 99999)))),
    mid_player_id=ProPlayerID(str((randint(10000, 99999)))),
    adc_player_id=ProPlayerID(str((randint(10000, 99999)))),
    support_player_id=ProPlayerID(str((randint(10000, 99999))))
)

fantasy_team_week_1: FantasyTeam = FantasyTeam(
    fantasy_league_id=fantasy_league_active_fixture.id,
    user_id=user_fixture.id,
    week=1,
    top_player_id=None,
    jungle_player_id=None,
    mid_player_id=None,
    adc_player_id=None,
    support_player_id=None
)

fantasy_team_week_2: FantasyTeam = FantasyTeam(
    fantasy_league_id=fantasy_league_active_fixture.id,
    user_id=user_fixture.id,
    week=2,
    top_player_id=None,
    jungle_player_id=None,
    mid_player_id=None,
    adc_player_id=None,
    support_player_id=None
)
