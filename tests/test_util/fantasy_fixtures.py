import uuid
import bcrypt

from fantasylol.schemas import fantasy_schemas

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
