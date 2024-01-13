import random
from datetime import datetime, timedelta
import pytz

from fantasylol.schemas import riot_data_schemas as schemas
from fantasylol.schemas.game_state import GameState

future_start_date = datetime.now(pytz.utc) + timedelta(days=5)
formatted_future_start_date = future_start_date.strftime("%Y-%m-%d")

future_end_date = datetime.now(pytz.utc) + timedelta(days=10)
formatted_future_end_date = future_end_date.strftime("%Y-%m-%d")

future_match_date = datetime.now(pytz.utc) + timedelta(days=7)
formatted_future_match_datetime = future_end_date.strftime("%Y-%m-%dT%H:%M:%SZ")


league_fixture = schemas.LeagueSchema(
    id=random.randint(100000, 999999),
    name="Mock Challengers",
    slug="mock-challengers-league",
    region="MOCKED REGION",
    image="http//:mocked-league-image.png",
    priority=1
)

tournament_fixture = schemas.TournamentSchema(
    id=random.randint(100000, 999999),
    slug="mock_slug_2023",
    start_date="2023-01-01",
    end_date="2023-02-03",
    league_id=league_fixture.id
)

future_tournament_fixture = schemas.TournamentSchema(
    id=random.randint(100000, 999999),
    slug="future_slug",
    start_date=formatted_future_start_date,
    end_date=formatted_future_end_date,
    league_id=league_fixture.id
)

team_1_fixture = schemas.ProfessionalTeamSchema(
    id=random.randint(100000, 999999),
    slug="mock-team-1",
    name="Mock Team 1",
    code="T1",
    image="http://mock-team-1-image.png",
    alternative_image="http://mock-team-1-alternative-image.png",
    background_image="http://mock-team-1-background.png",
    status="active",
    home_league=league_fixture.name
)

team_2_fixture = schemas.ProfessionalTeamSchema(
    id=random.randint(100000, 999999),
    slug="mock-team-2",
    name="Mock Team 2",
    code="T2",
    image="http://mock-team-2-image.png",
    alternative_image="http://mock-team-2-alternative-image.png",
    background_image="http://mock-team-2-background.png",
    status="active",
    home_league=league_fixture.name
)

match_fixture = schemas.MatchSchema(
    id=random.randint(100000, 999999),
    start_time="2023-01-03T15:00:00Z",
    block_name="mockBlockName",
    league_name=league_fixture.name,
    strategy_type="bestOf",
    strategy_count=3,
    tournament_id=tournament_fixture.id,
    team_1_name=team_1_fixture.name,
    team_2_name=team_2_fixture.name
)

future_match_fixture = schemas.MatchSchema(
    id=random.randint(100000, 999999),
    start_time=formatted_future_match_datetime,
    block_name="futureBlockName",
    league_name=league_fixture.name,
    strategy_type="bestOf",
    strategy_count=3,
    tournament_id=tournament_fixture.id,
    team_1_name=team_1_fixture.name,
    team_2_name=team_2_fixture.name
)

game_1_fixture_completed = schemas.GameSchema(
    id=random.randint(100000, 999999),
    state=GameState.COMPLETED,
    number=1,
    match_id=match_fixture.id
)

get_games_response_game_1_fixture = schemas.GetGamesResponseSchema(
    id=game_1_fixture_completed.id,
    state=game_1_fixture_completed.state
)

game_2_fixture_inprogress = schemas.GameSchema(
    id=random.randint(100000, 999999),
    state=GameState.INPROGRESS,
    number=2,
    match_id=match_fixture.id
)

game_3_fixture_unstarted = schemas.GameSchema(
    id=random.randint(100000, 999999),
    state=GameState.UNSTARTED,
    number=3,
    match_id=match_fixture.id
)

game_4_fixture_unneeded = schemas.GameSchema(
    id=random.randint(100000, 999999),
    state=GameState.UNNEEDED,
    number=4,
    match_id=match_fixture.id
)

player_1_fixture = schemas.ProfessionalPlayerSchema(
    id=random.randint(100000, 999999),
    summoner_name="MockerPlayer1",
    image="http://mocked-player-1.png",
    role="top",
    team_id=team_1_fixture.id
)

player_2_fixture = schemas.ProfessionalPlayerSchema(
    id=random.randint(100000, 999999),
    summoner_name="MockerPlayer2",
    image="http://mocked-player-2.png",
    role="jungle",
    team_id=team_1_fixture.id
)

player_3_fixture = schemas.ProfessionalPlayerSchema(
    id=random.randint(100000, 999999),
    summoner_name="MockerPlayer3",
    image="http://mocked-player-3.png",
    role="mid",
    team_id=team_1_fixture.id
)

player_4_fixture = schemas.ProfessionalPlayerSchema(
    id=random.randint(100000, 999999),
    summoner_name="MockerPlayer4",
    image="http://mocked-player-4.png",
    role="bottom",
    team_id=team_1_fixture.id
)

player_5_fixture = schemas.ProfessionalPlayerSchema(
    id=random.randint(100000, 999999),
    summoner_name="MockerPlayer5",
    image="http://mocked-player-5.png",
    role="support",
    team_id=team_1_fixture.id
)