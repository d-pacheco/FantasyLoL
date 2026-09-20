"""Integration tests for enriched player match history (DatabaseService level).

Seeds a self-consistent scenario (participant 1-5 => blue side) so that
side / opponent / win derivation can be verified. The shared riot_fixtures are
intentionally NOT used for side logic because their player->team assignments do
not line up with the blue/red team of the seeded games.
"""

import pytest

from src.common.schemas import riot_data_schemas as schemas
from src.common.schemas.riot_data_schemas import (
    GameState,
    MatchState,
    PlayerRole,
    ProPlayerID,
    ProTeamID,
    RiotGameID,
    RiotLeagueID,
    RiotMatchID,
    RiotTournamentID,
)


def _mk_stats(game_id, participant_id, **overrides):
    base = dict(
        game_id=game_id,
        participant_id=participant_id,
        kills=4,
        deaths=2,
        assists=6,
        total_gold=12000,
        creep_score=300,
        kill_participation=60,
        champion_damage_share=30,
        wards_placed=15,
        wards_destroyed=7,
    )
    base.update(overrides)
    return schemas.PlayerGameStats(**base)


@pytest.fixture
def match_history_scenario(db):
    """Two completed games for player_1 across two matches with different start times.

    - team_1 (code T1) is BLUE (participants 1-5), team_2 (code T2) is RED.
    - matchA (older) team_1 WINS; matchB (newer) team_1 LOSES.
    - player_1 is participant 1 (blue => team_1).
    Returns the seeded player id.
    """
    league = schemas.League(
        id=RiotLeagueID("900000000000000001"),
        name="Mock League",
        slug="mock-league",
        region="MOCK",
        image="http://league.png",
        priority=1,
        fantasy_available=True,
        scrape_enabled=True,
    )
    team_1 = schemas.ProfessionalTeam(
        id=ProTeamID("900000000000000010"),
        slug="team-1",
        name="Team One",
        code="T1",
        image="http://t1.png",
        alternative_image=None,
        background_image=None,
        status="active",
        home_league_name=league.name,
        home_league_region="MOCK",
    )
    team_2 = schemas.ProfessionalTeam(
        id=ProTeamID("900000000000000020"),
        slug="team-2",
        name="Team Two",
        code="T2",
        image="http://t2.png",
        alternative_image=None,
        background_image=None,
        status="active",
        home_league_name=league.name,
        home_league_region="MOCK",
    )
    tournament = schemas.Tournament(
        id=RiotTournamentID("900000000000000030"),
        slug="mock-tournament",
        start_date="2023-01-01",
        end_date="2023-02-01",
        league_id=league.id,
    )
    player = schemas.ProfessionalPlayer(
        id=ProPlayerID("900000000000000040"),
        summoner_name="MockStar",
        first_name="Mock",
        last_name="Star",
        image="http://player.png",
        role=PlayerRole.TOP,
        team_id=team_1.id,
        team_name=team_1.name,
        team_code=team_1.code,
        league_name=league.name,
    )

    def _match(match_id, start_time, winning_team, t1_wins, t2_wins):
        return schemas.Match(
            id=RiotMatchID(match_id),
            start_time=start_time,
            block_name="Regular Season",
            league_slug=league.slug,
            strategy_type="bestOf",
            strategy_count=1,
            tournament_id=tournament.id,
            team_1_name=team_1.name,
            team_2_name=team_2.name,
            has_games=True,
            state=MatchState.COMPLETED,
            team_1_wins=t1_wins,
            team_2_wins=t2_wins,
            winning_team=winning_team,
            team_1_image=team_1.image,
            team_2_image=team_2.image,
        )

    match_a = _match("900000000000000100", "2023-01-03T15:00:00Z", team_1.name, 1, 0)
    match_b = _match("900000000000000200", "2023-05-03T15:00:00Z", team_2.name, 0, 1)

    def _game(game_id, match_id):
        # blue_team=team_1 so participant 1 (blue) maps to team_1
        return schemas.Game(
            id=RiotGameID(game_id),
            state=GameState.COMPLETED,
            number=1,
            red_team=team_2.id,
            blue_team=team_1.id,
            match_id=RiotMatchID(match_id),
            has_game_data=True,
        )

    game_a = _game("900000000000000101", match_a.id)
    game_b = _game("900000000000000201", match_b.id)

    db.put_league(league)
    db.put_team(team_1)
    db.put_team(team_2)
    db.put_tournament(tournament)
    db.put_player(player)
    db.put_match(match_a)
    db.put_match(match_b)
    db.put_game(game_a)
    db.put_game(game_b)
    db.update_game_duration(game_a.id, 1800)  # 30 min
    db.update_game_duration(game_b.id, 2400)  # 40 min
    db.put_game_metadata(schemas.GameMetadata(game_id=game_a.id, patch_version="14.10"))
    db.put_game_metadata(schemas.GameMetadata(game_id=game_b.id, patch_version="14.18"))

    # player_1 = participant 1 in both games
    for g in (game_a, game_b):
        db.put_player_metadata(
            schemas.PlayerGameMetadata(
                game_id=g.id,
                player_id=player.id,
                participant_id=1,
                champion_id="ChampX",
                role=PlayerRole.TOP,
            )
        )
    db.put_player_stats(_mk_stats(game_a.id, 1, kills=2, deaths=1, assists=4, creep_score=270))
    db.put_player_stats(_mk_stats(game_b.id, 1, kills=6, deaths=3, assists=8, creep_score=360))

    # multi-kills for player in game_b (participant 1)
    db.put_game_multi_kill(game_b.id, 1, 1, "double")
    db.put_game_multi_kill(game_b.id, 1, 2, "triple")

    return player.id


def test_match_history_orders_by_start_time_desc(db, match_history_scenario):
    player_id = match_history_scenario
    history = db.get_player_match_history(player_id)

    assert [h.patch_version for h in history] == ["14.18", "14.10"]  # newest first


def test_match_history_enriched_fields(db, match_history_scenario):
    player_id = match_history_scenario
    history = db.get_player_match_history(player_id)
    newest = history[0]  # game_b / match_b

    assert newest.side == "blue"
    assert newest.opponent_code == "T2"
    assert newest.win is False  # team_1 lost match_b
    assert newest.duration_seconds == 2400
    assert newest.block_name == "Regular Season"
    assert newest.league_slug == "mock-league"
    assert sorted(newest.multi_kills) == ["double", "triple"]
    # cs/min = 360 / (2400/60) = 9.0 ; gold/min = 12000 / 40 = 300
    assert newest.cs_per_min == pytest.approx(9.0, abs=0.05)
    assert newest.gold_per_min == pytest.approx(300.0, abs=0.5)

    oldest = history[1]  # game_a / match_a
    assert oldest.win is True  # team_1 won match_a
    assert oldest.multi_kills == []


def test_match_history_empty_for_unknown_player(db, match_history_scenario):
    assert db.get_player_match_history(ProPlayerID("111111111111111111")) == []


def test_opponent_is_not_players_own_team_when_participant_side_inverted(db):
    """Regression: the player's side/opponent must come from their actual team
    (game_teams), not from the participant-id -> side convention.

    Here the player is participant 1 (which the old code assumed was 'blue') but
    the player's team is on the RED side of the game. The opponent must be the
    other team, never the player's own team.
    """
    league = schemas.League(
        id=RiotLeagueID("910000000000000001"),
        name="Inv League",
        slug="inv-league",
        region="MOCK",
        image="http://l.png",
        priority=1,
        fantasy_available=True,
        scrape_enabled=True,
    )
    home = schemas.ProfessionalTeam(
        id=ProTeamID("910000000000000010"),
        slug="home",
        name="Home Team",
        code="HOME",
        image="http://h.png",
        alternative_image=None,
        background_image=None,
        status="active",
        home_league_name=league.name,
        home_league_region="MOCK",
    )
    away = schemas.ProfessionalTeam(
        id=ProTeamID("910000000000000020"),
        slug="away",
        name="Away Team",
        code="AWAY",
        image="http://a.png",
        alternative_image=None,
        background_image=None,
        status="active",
        home_league_name=league.name,
        home_league_region="MOCK",
    )
    tournament = schemas.Tournament(
        id=RiotTournamentID("910000000000000030"),
        slug="inv-tournament",
        start_date="2023-01-01",
        end_date="2023-02-01",
        league_id=league.id,
    )
    player = schemas.ProfessionalPlayer(
        id=ProPlayerID("910000000000000040"),
        summoner_name="Inverted",
        first_name="In",
        last_name="Verted",
        image="http://p.png",
        role=PlayerRole.BOTTOM,
        team_id=home.id,
        team_name=home.name,
        team_code=home.code,
        league_name=league.name,
    )
    match = schemas.Match(
        id=RiotMatchID("910000000000000100"),
        start_time="2023-03-03T15:00:00Z",
        block_name="Regular Season",
        league_slug=league.slug,
        strategy_type="bestOf",
        strategy_count=1,
        tournament_id=tournament.id,
        team_1_name=home.name,
        team_2_name=away.name,
        has_games=True,
        state=MatchState.COMPLETED,
        team_1_wins=1,
        team_2_wins=0,
        winning_team=home.name,
        team_1_image=home.image,
        team_2_image=away.image,
    )
    # KEY: player's team (home) is on the RED side, but the player is participant 1
    # (which the buggy convention treated as blue).
    game = schemas.Game(
        id=RiotGameID("910000000000000101"),
        state=GameState.COMPLETED,
        number=1,
        red_team=home.id,
        blue_team=away.id,
        match_id=match.id,
        has_game_data=True,
    )

    db.put_league(league)
    db.put_team(home)
    db.put_team(away)
    db.put_tournament(tournament)
    db.put_player(player)
    db.put_match(match)
    db.put_game(game)
    db.update_game_duration(game.id, 1800)
    db.put_game_metadata(schemas.GameMetadata(game_id=game.id, patch_version="14.20"))
    db.put_player_metadata(
        schemas.PlayerGameMetadata(
            game_id=game.id,
            player_id=player.id,
            participant_id=1,
            champion_id="ChampY",
            role=PlayerRole.BOTTOM,
        )
    )
    db.put_player_stats(_mk_stats(game.id, 1))

    history = db.get_player_match_history(player.id)
    assert len(history) == 1
    entry = history[0]
    assert entry.opponent_code == "AWAY"  # NOT "HOME"
    assert entry.opponent_name == "Away Team"
    assert entry.side == "red"  # actual game_teams side, not participant-derived
    assert entry.win is True
