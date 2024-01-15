from fantasylol.schemas import riot_data_schemas
from tests.test_util import test_fixtures
from tests.test_util import db_util


def create_completed_game_in_db() -> riot_data_schemas.GameSchema:
    completed_game = test_fixtures.game_1_fixture_completed
    db_util.save_game(completed_game)
    return completed_game


def create_inprogress_game_in_db() -> riot_data_schemas.GameSchema:
    inprogress_game = test_fixtures.game_2_fixture_inprogress
    db_util.save_game(inprogress_game)
    return inprogress_game


def create_unstarted_game_in_db() -> riot_data_schemas.GameSchema:
    unstarted_game = test_fixtures.game_3_fixture_unstarted
    db_util.save_game(unstarted_game)
    return unstarted_game


def create_unneeded_game_in_db() -> riot_data_schemas.GameSchema:
    unneeded_game = test_fixtures.game_4_fixture_unneeded
    db_util.save_game(unneeded_game)
    return unneeded_game
