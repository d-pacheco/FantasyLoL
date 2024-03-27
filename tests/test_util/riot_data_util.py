from common.schemas import riot_data_schemas
from tests.test_util import test_fixtures
from tests.test_util import db_util


def create_completed_game_in_db() -> riot_data_schemas.Game:
    completed_game = test_fixtures.game_1_fixture_completed
    db_util.save_game(completed_game)
    return completed_game


def create_inprogress_game_in_db() -> riot_data_schemas.Game:
    inprogress_game = test_fixtures.game_2_fixture_inprogress
    db_util.save_game(inprogress_game)
    return inprogress_game


def create_unstarted_game_in_db() -> riot_data_schemas.Game:
    unstarted_game = test_fixtures.game_3_fixture_unstarted
    db_util.save_game(unstarted_game)
    return unstarted_game


def create_unneeded_game_in_db() -> riot_data_schemas.Game:
    unneeded_game = test_fixtures.game_4_fixture_unneeded
    db_util.save_game(unneeded_game)
    return unneeded_game


def create_completed_tournament_in_db() -> riot_data_schemas.Tournament:
    completed_tournament = test_fixtures.tournament_fixture
    db_util.save_tournament(completed_tournament)
    return completed_tournament


def create_upcoming_tournament_in_db() -> riot_data_schemas.Tournament:
    upcoming_tournament = test_fixtures.future_tournament_fixture
    db_util.save_tournament(upcoming_tournament)
    return upcoming_tournament


def create_active_tournament_in_db() -> riot_data_schemas.Tournament:
    active_tournament = test_fixtures.active_tournament_fixture
    db_util.save_tournament(active_tournament)
    return active_tournament


def create_professional_team_in_db() -> riot_data_schemas.ProfessionalTeam:
    team = test_fixtures.team_1_fixture
    db_util.save_team(team)
    return team


def create_professional_player_in_db() -> riot_data_schemas.ProfessionalPlayer:
    player = test_fixtures.player_1_fixture
    db_util.save_player(player)
    return player


def create_match_in_db() -> riot_data_schemas.Match:
    match = test_fixtures.match_fixture
    db_util.save_match(match)
    return match
