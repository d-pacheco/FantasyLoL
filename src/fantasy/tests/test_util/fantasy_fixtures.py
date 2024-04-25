import uuid
import bcrypt

from src.common.schemas import fantasy_schemas

user_password = "WeakTestPw"
salt = bcrypt.gensalt()
user_hashed_password = bcrypt.hashpw(str.encode(user_password), salt)

user_create_fixture = fantasy_schemas.UserCreate(
    username="MyUsername",
    email="MyEmail@gmail.com",
    password=user_password
)

user_login_fixture = fantasy_schemas.UserLogin(
    username=user_create_fixture.username,
    password=user_password
)

user_fixture = fantasy_schemas.User(
    id=str(uuid.uuid4()),
    username=user_create_fixture.username,
    email=user_create_fixture.email,
    password=user_hashed_password
)

user_2_fixture = fantasy_schemas.User(
    id=str(uuid.uuid4()),
    username="user2",
    email="user2@email.com",
    password=user_hashed_password
)

user_3_fixture = fantasy_schemas.User(
    id=str(uuid.uuid4()),
    username="user3",
    email="user3@email.com",
    password=user_hashed_password
)

fantasy_league_settings_fixture = fantasy_schemas.FantasyLeagueSettings(
    name="Fantasy League 1",
    number_of_teams=6
)

fantasy_league_fixture = fantasy_schemas.FantasyLeague(
    id=str(uuid.uuid4()),
    owner_id=user_fixture.id,
    status=fantasy_schemas.FantasyLeagueStatus.PRE_DRAFT,
    name=fantasy_league_settings_fixture.name,
    number_of_teams=fantasy_league_settings_fixture.number_of_teams
)

fantasy_league_scoring_settings_fixture = fantasy_schemas.FantasyLeagueScoringSettings(
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

fantasy_team_week_1 = fantasy_schemas.FantasyTeam(
    fantasy_league_id=fantasy_league_fixture.id,
    user_id=user_fixture.id,
    week=1,
    top_player_id=None,
    jungle_player_id=None,
    mid_player_id=None,
    adc_player_id=None,
    support_player_id=None
)

fantasy_team_week_2 = fantasy_schemas.FantasyTeam(
    fantasy_league_id=fantasy_league_fixture.id,
    user_id=user_fixture.id,
    week=2,
    top_player_id=None,
    jungle_player_id=None,
    mid_player_id=None,
    adc_player_id=None,
    support_player_id=None
)
