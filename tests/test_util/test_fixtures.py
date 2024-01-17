import random
from datetime import datetime, timedelta
import pytz

from fantasylol.schemas import riot_data_schemas as schemas
from fantasylol.schemas.riot_data_schemas import GameState

past_start_date = datetime.now(pytz.utc) - timedelta(days=5)
formatted_past_start_date = past_start_date.strftime("%Y-%m-%d")

future_start_date = datetime.now(pytz.utc) + timedelta(days=5)
formatted_future_start_date = future_start_date.strftime("%Y-%m-%d")

future_end_date = datetime.now(pytz.utc) + timedelta(days=10)
formatted_future_end_date = future_end_date.strftime("%Y-%m-%d")

future_match_date = datetime.now(pytz.utc) + timedelta(days=7)
formatted_future_match_datetime = future_end_date.strftime("%Y-%m-%dT%H:%M:%SZ")


def generate_random_id():
    return str(random.randint(100000000000000000, 999999999999999999))


league_fixture = schemas.League(
    id=generate_random_id(),
    name="Mock Challengers",
    slug="mock-challengers-league",
    region="MOCKED REGION",
    image="http//:mocked-league-image.png",
    priority=1
)

tournament_fixture = schemas.Tournament(
    id=generate_random_id(),
    slug="mock_slug_2023",
    start_date="2023-01-01",
    end_date="2023-02-03",
    league_id=league_fixture.id
)

future_tournament_fixture = schemas.Tournament(
    id=generate_random_id(),
    slug="future_slug",
    start_date=formatted_future_start_date,
    end_date=formatted_future_end_date,
    league_id=league_fixture.id
)

active_tournament_fixture = schemas.Tournament(
    id=generate_random_id(),
    slug="active_slug",
    start_date=formatted_past_start_date,
    end_date=formatted_future_end_date,
    league_id=league_fixture.id
)

team_1_fixture = schemas.ProfessionalTeam(
    id=generate_random_id(),
    slug="mock-team-1",
    name="Mock Team 1",
    code="T1",
    image="http://mock-team-1-image.png",
    alternative_image="http://mock-team-1-alternative-image.png",
    background_image="http://mock-team-1-background.png",
    status="active",
    home_league=league_fixture.name
)

team_2_fixture = schemas.ProfessionalTeam(
    id=generate_random_id(),
    slug="mock-team-2",
    name="Mock Team 2",
    code="T2",
    image="http://mock-team-2-image.png",
    alternative_image="http://mock-team-2-alternative-image.png",
    background_image="http://mock-team-2-background.png",
    status="active",
    home_league=league_fixture.name
)

match_fixture = schemas.Match(
    id=generate_random_id(),
    start_time="2023-01-03T15:00:00Z",
    block_name="mockBlockName",
    league_slug=league_fixture.slug,
    strategy_type="bestOf",
    strategy_count=3,
    tournament_id=tournament_fixture.id,
    team_1_name=team_1_fixture.name,
    team_2_name=team_2_fixture.name
)

future_match_fixture = schemas.Match(
    id=generate_random_id(),
    start_time=formatted_future_match_datetime,
    block_name="futureBlockName",
    league_slug=league_fixture.slug,
    strategy_type="bestOf",
    strategy_count=3,
    tournament_id=tournament_fixture.id,
    team_1_name=team_1_fixture.name,
    team_2_name=team_2_fixture.name
)

game_1_fixture_completed = schemas.Game(
    id=generate_random_id(),
    state=GameState.COMPLETED,
    number=1,
    match_id=match_fixture.id
)

get_games_response_game_1_fixture = schemas.GetGamesResponseSchema(
    id=game_1_fixture_completed.id,
    state=game_1_fixture_completed.state
)

game_2_fixture_inprogress = schemas.Game(
    id=generate_random_id(),
    state=GameState.INPROGRESS,
    number=2,
    match_id=match_fixture.id
)

game_3_fixture_unstarted = schemas.Game(
    id=generate_random_id(),
    state=GameState.UNSTARTED,
    number=3,
    match_id=match_fixture.id
)

game_4_fixture_unneeded = schemas.Game(
    id=generate_random_id(),
    state=GameState.UNNEEDED,
    number=4,
    match_id=match_fixture.id
)

player_1_fixture = schemas.ProfessionalPlayer(
    id=generate_random_id(),
    summoner_name="MockerPlayer1",
    image="http://mocked-player-1.png",
    role="top",
    team_id=team_1_fixture.id
)

player_2_fixture = schemas.ProfessionalPlayer(
    id=generate_random_id(),
    summoner_name="MockerPlayer2",
    image="http://mocked-player-2.png",
    role="jungle",
    team_id=team_1_fixture.id
)

player_3_fixture = schemas.ProfessionalPlayer(
    id=generate_random_id(),
    summoner_name="MockerPlayer3",
    image="http://mocked-player-3.png",
    role="mid",
    team_id=team_1_fixture.id
)

player_4_fixture = schemas.ProfessionalPlayer(
    id=generate_random_id(),
    summoner_name="MockerPlayer4",
    image="http://mocked-player-4.png",
    role="bottom",
    team_id=team_1_fixture.id
)

player_5_fixture = schemas.ProfessionalPlayer(
    id=generate_random_id(),
    summoner_name="MockerPlayer5",
    image="http://mocked-player-5.png",
    role="support",
    team_id=team_1_fixture.id
)

player_6_fixture = schemas.ProfessionalPlayer(
    id=generate_random_id(),
    summoner_name="MockerPlayer6",
    image="http://mocked-player-6.png",
    role="top",
    team_id=team_2_fixture.id
)

player_7_fixture = schemas.ProfessionalPlayer(
    id=generate_random_id(),
    summoner_name="MockerPlayer7",
    image="http://mocked-player-7.png",
    role="jungle",
    team_id=team_2_fixture.id
)

player_8_fixture = schemas.ProfessionalPlayer(
    id=generate_random_id(),
    summoner_name="MockerPlayer8",
    image="http://mocked-player-8.png",
    role="mid",
    team_id=team_2_fixture.id
)

player_9_fixture = schemas.ProfessionalPlayer(
    id=generate_random_id(),
    summoner_name="MockerPlayer9",
    image="http://mocked-player-9.png",
    role="bottom",
    team_id=team_2_fixture.id
)

player_10_fixture = schemas.ProfessionalPlayer(
    id=generate_random_id(),
    summoner_name="MockerPlayer10",
    image="http://mocked-player-10.png",
    role="support",
    team_id=team_2_fixture.id
)

player_1_game_metadata_fixture = schemas.PlayerGameMetadata(
    game_id=game_1_fixture_completed.id,
    player_id=player_1_fixture.id,
    participant_id=1,
    champion_id="champion1",
    role="top"
)

player_2_game_metadata_fixture = schemas.PlayerGameMetadata(
    game_id=game_1_fixture_completed.id,
    player_id=player_2_fixture.id,
    participant_id=2,
    champion_id="champion2",
    role="jungle"
)

player_3_game_metadata_fixture = schemas.PlayerGameMetadata(
    game_id=game_1_fixture_completed.id,
    player_id=player_3_fixture.id,
    participant_id=3,
    champion_id="champion3",
    role="mid"
)

player_4_game_metadata_fixture = schemas.PlayerGameMetadata(
    game_id=game_1_fixture_completed.id,
    player_id=player_4_fixture.id,
    participant_id=4,
    champion_id="champion4",
    role="bottom"
)

player_5_game_metadata_fixture = schemas.PlayerGameMetadata(
    game_id=game_1_fixture_completed.id,
    player_id=player_5_fixture.id,
    participant_id=5,
    champion_id="champion5",
    role="support"
)

player_6_game_metadata_fixture = schemas.PlayerGameMetadata(
    game_id=game_1_fixture_completed.id,
    player_id=player_6_fixture.id,
    participant_id=6,
    champion_id="champion6",
    role="top"
)

player_7_game_metadata_fixture = schemas.PlayerGameMetadata(
    game_id=game_1_fixture_completed.id,
    player_id=player_7_fixture.id,
    participant_id=7,
    champion_id="champion7",
    role="jungle"
)

player_8_game_metadata_fixture = schemas.PlayerGameMetadata(
    game_id=game_1_fixture_completed.id,
    player_id=player_8_fixture.id,
    participant_id=8,
    champion_id="champion8",
    role="mid"
)

player_9_game_metadata_fixture = schemas.PlayerGameMetadata(
    game_id=game_1_fixture_completed.id,
    player_id=player_9_fixture.id,
    participant_id=9,
    champion_id="champion9",
    role="bottom"
)

player_10_game_metadata_fixture = schemas.PlayerGameMetadata(
    game_id=game_1_fixture_completed.id,
    player_id=player_10_fixture.id,
    participant_id=10,
    champion_id="champion10",
    role="support"
)

player_1_game_stats_fixture = schemas.PlayerGameStats(
    game_id=game_1_fixture_completed.id,
    participant_id=player_1_game_metadata_fixture.participant_id,
    kills=random.randint(1, 5),
    deaths=random.randint(1, 5),
    assists=random.randint(1, 5),
    total_gold=random.randint(5000, 20000),
    creep_score=random.randint(100, 250),
    kill_participation=20,
    champion_damage_share=20,
    wards_placed=random.randint(10, 20),
    wards_destroyed=random.randint(10, 20)
)

player_2_game_stats_fixture = schemas.PlayerGameStats(
    game_id=game_1_fixture_completed.id,
    participant_id=player_2_game_metadata_fixture.participant_id,
    kills=random.randint(1, 5),
    deaths=random.randint(1, 5),
    assists=random.randint(1, 5),
    total_gold=random.randint(5000, 20000),
    creep_score=random.randint(100, 250),
    kill_participation=20,
    champion_damage_share=20,
    wards_placed=random.randint(10, 20),
    wards_destroyed=random.randint(10, 20)
)

player_3_game_stats_fixture = schemas.PlayerGameStats(
    game_id=game_1_fixture_completed.id,
    participant_id=player_3_game_metadata_fixture.participant_id,
    kills=random.randint(1, 5),
    deaths=random.randint(1, 5),
    assists=random.randint(1, 5),
    total_gold=random.randint(5000, 20000),
    creep_score=random.randint(100, 250),
    kill_participation=20,
    champion_damage_share=20,
    wards_placed=random.randint(10, 20),
    wards_destroyed=random.randint(10, 20)
)

player_4_game_stats_fixture = schemas.PlayerGameStats(
    game_id=game_1_fixture_completed.id,
    participant_id=player_4_game_metadata_fixture.participant_id,
    kills=random.randint(1, 5),
    deaths=random.randint(1, 5),
    assists=random.randint(1, 5),
    total_gold=random.randint(5000, 20000),
    creep_score=random.randint(100, 250),
    kill_participation=20,
    champion_damage_share=20,
    wards_placed=random.randint(10, 20),
    wards_destroyed=random.randint(10, 20)
)

player_5_game_stats_fixture = schemas.PlayerGameStats(
    game_id=game_1_fixture_completed.id,
    participant_id=player_5_game_metadata_fixture.participant_id,
    kills=random.randint(1, 5),
    deaths=random.randint(1, 5),
    assists=random.randint(1, 5),
    total_gold=random.randint(5000, 20000),
    creep_score=random.randint(100, 250),
    kill_participation=20,
    champion_damage_share=20,
    wards_placed=random.randint(10, 20),
    wards_destroyed=random.randint(10, 20)
)

player_6_game_stats_fixture = schemas.PlayerGameStats(
    game_id=game_1_fixture_completed.id,
    participant_id=player_6_game_metadata_fixture.participant_id,
    kills=random.randint(1, 5),
    deaths=random.randint(1, 5),
    assists=random.randint(1, 5),
    total_gold=random.randint(5000, 20000),
    creep_score=random.randint(100, 250),
    kill_participation=20,
    champion_damage_share=20,
    wards_placed=random.randint(10, 20),
    wards_destroyed=random.randint(10, 20)
)

player_7_game_stats_fixture = schemas.PlayerGameStats(
    game_id=game_1_fixture_completed.id,
    participant_id=player_7_game_metadata_fixture.participant_id,
    kills=random.randint(1, 5),
    deaths=random.randint(1, 5),
    assists=random.randint(1, 5),
    total_gold=random.randint(5000, 20000),
    creep_score=random.randint(100, 250),
    kill_participation=20,
    champion_damage_share=20,
    wards_placed=random.randint(10, 20),
    wards_destroyed=random.randint(10, 20)
)

player_8_game_stats_fixture = schemas.PlayerGameStats(
    game_id=game_1_fixture_completed.id,
    participant_id=player_8_game_metadata_fixture.participant_id,
    kills=random.randint(1, 5),
    deaths=random.randint(1, 5),
    assists=random.randint(1, 5),
    total_gold=random.randint(5000, 20000),
    creep_score=random.randint(100, 250),
    kill_participation=20,
    champion_damage_share=20,
    wards_placed=random.randint(10, 20),
    wards_destroyed=random.randint(10, 20)
)

player_9_game_stats_fixture = schemas.PlayerGameStats(
    game_id=game_1_fixture_completed.id,
    participant_id=player_9_game_metadata_fixture.participant_id,
    kills=random.randint(1, 5),
    deaths=random.randint(1, 5),
    assists=random.randint(1, 5),
    total_gold=random.randint(5000, 20000),
    creep_score=random.randint(100, 250),
    kill_participation=20,
    champion_damage_share=20,
    wards_placed=random.randint(10, 20),
    wards_destroyed=random.randint(10, 20)
)

player_10_game_stats_fixture = schemas.PlayerGameStats(
    game_id=game_1_fixture_completed.id,
    participant_id=player_10_game_metadata_fixture.participant_id,
    kills=random.randint(1, 5),
    deaths=random.randint(1, 5),
    assists=random.randint(1, 5),
    total_gold=random.randint(5000, 20000),
    creep_score=random.randint(100, 250),
    kill_participation=20,
    champion_damage_share=20,
    wards_placed=random.randint(10, 20),
    wards_destroyed=random.randint(10, 20)
)
