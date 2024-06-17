from src.common.schemas.riot_data_schemas import (
    Game,
    Tournament,
    ProfessionalTeam,
    ProfessionalPlayer,
    Match
)
from src.db.crud import put_game, put_match, put_tournament, put_player, put_team

from tests.test_util import riot_fixtures


def create_completed_game_in_db() -> Game:
    completed_game = riot_fixtures.game_1_fixture_completed
    put_game(completed_game)
    return completed_game


def create_inprogress_game_in_db() -> Game:
    inprogress_game = riot_fixtures.game_2_fixture_inprogress
    put_game(inprogress_game)
    return inprogress_game


def create_unstarted_game_in_db() -> Game:
    unstarted_game = riot_fixtures.game_3_fixture_unstarted
    put_game(unstarted_game)
    return unstarted_game


def create_unneeded_game_in_db() -> Game:
    unneeded_game = riot_fixtures.game_4_fixture_unneeded
    put_game(unneeded_game)
    return unneeded_game


def create_completed_tournament_in_db() -> Tournament:
    completed_tournament = riot_fixtures.tournament_fixture
    put_tournament(completed_tournament)
    return completed_tournament


def create_upcoming_tournament_in_db() -> Tournament:
    upcoming_tournament = riot_fixtures.future_tournament_fixture
    put_tournament(upcoming_tournament)
    return upcoming_tournament


def create_active_tournament_in_db() -> Tournament:
    active_tournament = riot_fixtures.active_tournament_fixture
    put_tournament(active_tournament)
    return active_tournament


def create_professional_team_in_db() -> ProfessionalTeam:
    team = riot_fixtures.team_1_fixture
    put_team(team)
    return team


def create_professional_player_in_db() -> ProfessionalPlayer:
    player = riot_fixtures.player_1_fixture
    put_player(player)
    return player


def create_match_in_db() -> Match:
    match = riot_fixtures.match_fixture
    put_match(match)
    return match
