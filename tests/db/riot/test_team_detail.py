"""Integration tests for team detail DAO methods (match history + stat lines)."""

import pytest

from src.common.schemas import riot_data_schemas as schemas
from src.common.schemas.riot_data_schemas import (
    GameState,
    MatchState,
    ProTeamID,
    RiotGameID,
    RiotLeagueID,
    RiotMatchID,
    RiotTournamentID,
)


def _team(team_id, name, code):
    return schemas.ProfessionalTeam(
        id=ProTeamID(team_id),
        slug=code.lower(),
        name=name,
        code=code,
        image=f"http://{code}.png",
        alternative_image=None,
        background_image=None,
        status="active",
        home_league_name="Mock League",
        home_league_region="MOCK",
    )


@pytest.fixture
def team_detail_scenario(db):
    """team_home plays 2 matches: matchA (older) beats OPP 2-1, matchB (newer) loses to SUB 0-2.
    Two games in matchA carry team_home stats + dragons.
    Returns team_home id.
    """
    league = schemas.League(
        id=RiotLeagueID("920000000000000001"),
        name="Mock League",
        slug="mock-league",
        region="MOCK",
        image="http://l.png",
        priority=1,
        fantasy_available=True,
        scrape_enabled=True,
    )
    home = _team("920000000000000010", "Home Team", "HOME")
    opp = _team("920000000000000020", "Opp Team", "OPP")
    sub = _team("920000000000000030", "Sub Team", "SUB")
    tournament = schemas.Tournament(
        id=RiotTournamentID("920000000000000040"),
        slug="mock-tournament",
        start_date="2023-01-01",
        end_date="2023-02-01",
        league_id=league.id,
    )

    def _match(match_id, start_time, opp_name, winner, home_wins, opp_wins):
        return schemas.Match(
            id=RiotMatchID(match_id),
            start_time=start_time,
            block_name="Regular Season",
            league_slug=league.slug,
            strategy_type="bestOf",
            strategy_count=3,
            tournament_id=tournament.id,
            team_1_name=home.name,
            team_2_name=opp_name,
            has_games=True,
            state=MatchState.COMPLETED,
            team_1_wins=home_wins,
            team_2_wins=opp_wins,
            winning_team=winner,
            team_1_image=home.image,
            team_2_image="http://x.png",
        )

    match_a = _match("920000000000000100", "2023-01-03T15:00:00Z", opp.name, home.name, 2, 1)
    match_b = _match("920000000000000200", "2023-05-03T15:00:00Z", sub.name, sub.name, 0, 2)

    game_a1 = schemas.Game(
        id=RiotGameID("920000000000000101"),
        state=GameState.COMPLETED,
        number=1,
        red_team=opp.id,
        blue_team=home.id,
        match_id=match_a.id,
        has_game_data=True,
    )
    game_a2 = schemas.Game(
        id=RiotGameID("920000000000000102"),
        state=GameState.COMPLETED,
        number=2,
        red_team=opp.id,
        blue_team=home.id,
        match_id=match_a.id,
        has_game_data=True,
    )

    db.put_league(league)
    db.put_team(home)
    db.put_team(opp)
    db.put_team(sub)
    db.put_tournament(tournament)
    db.put_match(match_a)
    db.put_match(match_b)
    db.put_game(game_a1)
    db.put_game(game_a2)

    db.put_team_stats(
        schemas.TeamGameStats(
            game_id=game_a1.id,
            team_id=home.id,
            total_gold=60000,
            inhibitors=1,
            towers=8,
            barons=1,
            total_kills=15,
        )
    )
    db.put_team_stats(
        schemas.TeamGameStats(
            game_id=game_a2.id,
            team_id=home.id,
            total_gold=50000,
            inhibitors=1,
            towers=6,
            barons=0,
            total_kills=10,
        )
    )
    # dragons: 3 in game_a1, 1 in game_a2 for home
    for n in range(1, 4):
        db.put_game_dragon(
            schemas.GameDragons(
                game_id=game_a1.id, dragon_number=n, team_id=home.id, dragon_type="infernal"
            )
        )
    db.put_game_dragon(
        schemas.GameDragons(
            game_id=game_a2.id, dragon_number=1, team_id=home.id, dragon_type="ocean"
        )
    )

    return home.id


def test_team_match_history_orders_and_resolves_opponent(db, team_detail_scenario):
    team_id = team_detail_scenario
    history = db.get_team_match_history(team_id)

    assert len(history) == 2
    newest, oldest = history[0], history[1]

    # newest = matchB (loss to SUB 0-2)
    assert newest.opponent_code == "SUB"
    assert newest.win is False
    assert newest.team_score == 0
    assert newest.opponent_score == 2
    assert newest.strategy_count == 3

    # oldest = matchA (win vs OPP 2-1)
    assert oldest.opponent_code == "OPP"
    assert oldest.win is True
    assert oldest.team_score == 2
    assert oldest.opponent_score == 1


def test_team_match_history_opponent_never_self(db, team_detail_scenario):
    team_id = team_detail_scenario
    history = db.get_team_match_history(team_id)
    assert all(h.opponent_code != "HOME" for h in history)


def test_team_match_history_empty_for_unknown_team(db, team_detail_scenario):
    assert db.get_team_match_history(ProTeamID("111111111111111111")) == []


def test_team_game_stat_lines_include_dragon_counts(db, team_detail_scenario):
    team_id = team_detail_scenario
    lines = db.get_team_game_stat_lines(team_id)

    assert len(lines) == 2
    by_kills = sorted(lines, key=lambda x: x["total_kills"])
    assert by_kills[0]["total_kills"] == 10
    assert by_kills[0]["dragons"] == 1
    assert by_kills[1]["total_kills"] == 15
    assert by_kills[1]["dragons"] == 3
    assert by_kills[1]["towers"] == 8
    assert by_kills[1]["barons"] == 1
