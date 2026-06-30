import pytest

from src.fantasy.scoring.engine import compute_player_score
from src.common.schemas.fantasy_schemas import FantasyLeagueScoringSettings


@pytest.fixture
def default_weights():
    return FantasyLeagueScoringSettings(
        fantasy_league_id=None,
        kills=3,
        deaths=-1,
        assists=2,
        cspm=1.0,
        wards_placed=0.1,
        wards_destroyed=0.2,
        kill_participation=10,
        damage_percentage=5,
        double_kill=1.0,
        triple_kill=2.0,
        quadra_kill=4.0,
        penta_kill=10.0,
        match_win=5.0,
        match_sweep=5.0,
        dragon=1.0,
        elder_dragon=3.0,
        baron=2.0,
        tower=1.0,
        inhibitor=2.0,
        soul=4.0,
    )


class TestComputePlayerScore:
    def test_basic_stat_scoring_single_game(self, default_weights):
        """Single game: stats × weights, no averaging needed."""
        game_stats = [
            {
                "kills": 8,
                "deaths": 2,
                "assists": 5,
                "creep_score": 200,
                "wards_placed": 10,
                "wards_destroyed": 5,
                "kill_participation": 70,
                "champion_damage_share": 30,
            }
        ]
        game_durations = [1800]  # 30 minutes
        multi_kills = []

        result = compute_player_score(game_stats, game_durations, multi_kills, default_weights)

        assert result["total"] == pytest.approx(
            8 * 3          # kills
            + 2 * -1       # deaths
            + 5 * 2        # assists
            + (200 / 30) * 1.0  # cspm
            + 10 * 0.1    # wards_placed
            + 5 * 0.2     # wards_destroyed
            + 70 * 10     # kill_participation
            + 30 * 5      # damage_percentage
        , rel=1e-4)
        assert "kills" in result["breakdown"]
        assert result["breakdown"]["kills"] == pytest.approx(24.0)
        assert result["breakdown"]["deaths"] == pytest.approx(-2.0)

    def test_per_game_averaging_across_two_games(self, default_weights):
        """Stats should be summed then divided by number of games."""
        game_stats = [
            {
                "kills": 6, "deaths": 2, "assists": 4,
                "creep_score": 180, "wards_placed": 8,
                "wards_destroyed": 4, "kill_participation": 60,
                "champion_damage_share": 25,
            },
            {
                "kills": 10, "deaths": 4, "assists": 6,
                "creep_score": 220, "wards_placed": 12,
                "wards_destroyed": 6, "kill_participation": 80,
                "champion_damage_share": 35,
            },
        ]
        game_durations = [1800, 2400]  # 30 min, 40 min
        multi_kills = []

        result = compute_player_score(game_stats, game_durations, multi_kills, default_weights)

        # Averaged stats: kills=(6+10)/2=8, deaths=(2+4)/2=3, assists=(4+6)/2=5
        # cspm: game1=180/30=6, game2=220/40=5.5, avg=(6+5.5)/2=5.75
        assert result["breakdown"]["kills"] == pytest.approx(8 * 3)
        assert result["breakdown"]["deaths"] == pytest.approx(3 * -1)
        assert result["breakdown"]["assists"] == pytest.approx(5 * 2)
        assert result["breakdown"]["cspm"] == pytest.approx(5.75 * 1.0)

    def test_cspm_skipped_for_zero_duration(self, default_weights):
        """If game duration is 0, CSPM for that game should be excluded."""
        game_stats = [
            {
                "kills": 5, "deaths": 1, "assists": 3,
                "creep_score": 200, "wards_placed": 5,
                "wards_destroyed": 2, "kill_participation": 50,
                "champion_damage_share": 20,
            },
        ]
        game_durations = [0]
        multi_kills = []

        result = compute_player_score(game_stats, game_durations, multi_kills, default_weights)

        assert result["breakdown"]["cspm"] == 0.0

    def test_multi_kill_scoring(self, default_weights):
        """Multi-kills counted by type, averaged per game."""
        game_stats = [
            {
                "kills": 10, "deaths": 0, "assists": 0,
                "creep_score": 0, "wards_placed": 0,
                "wards_destroyed": 0, "kill_participation": 0,
                "champion_damage_share": 0,
            },
        ]
        game_durations = [1800]
        multi_kills = [
            {"kill_type": "Double", "game_index": 0},
            {"kill_type": "Double", "game_index": 0},
            {"kill_type": "Triple", "game_index": 0},
            {"kill_type": "Penta", "game_index": 0},
        ]

        result = compute_player_score(game_stats, game_durations, multi_kills, default_weights)

        assert result["breakdown"]["double_kill"] == pytest.approx(2 * 1.0)
        assert result["breakdown"]["triple_kill"] == pytest.approx(1 * 2.0)
        assert result["breakdown"]["penta_kill"] == pytest.approx(1 * 10.0)
        assert result["breakdown"]["quadra_kill"] == pytest.approx(0.0)

    def test_multi_kills_averaged_across_games(self, default_weights):
        """Multi-kills across multiple games should be averaged per game."""
        game_stats = [
            {"kills": 5, "deaths": 0, "assists": 0, "creep_score": 0,
             "wards_placed": 0, "wards_destroyed": 0, "kill_participation": 0,
             "champion_damage_share": 0},
            {"kills": 5, "deaths": 0, "assists": 0, "creep_score": 0,
             "wards_placed": 0, "wards_destroyed": 0, "kill_participation": 0,
             "champion_damage_share": 0},
        ]
        game_durations = [1800, 1800]
        multi_kills = [
            {"kill_type": "Double", "game_index": 0},
            {"kill_type": "Double", "game_index": 0},
            {"kill_type": "Double", "game_index": 1},
        ]

        result = compute_player_score(game_stats, game_durations, multi_kills, default_weights)

        # 3 doubles across 2 games → avg 1.5 per game → 1.5 × 1.0 = 1.5
        assert result["breakdown"]["double_kill"] == pytest.approx(1.5 * 1.0)

    def test_empty_game_stats_returns_zeros(self, default_weights):
        """No games played should return 0 total and all-zero breakdown."""
        result = compute_player_score([], [], [], default_weights)

        assert result["total"] == 0.0
        assert result["breakdown"]["kills"] == 0.0
        assert result["breakdown"]["cspm"] == 0.0
