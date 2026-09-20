"""Unit tests for player profile aggregation logic (mocked DatabaseService)."""

from unittest.mock import MagicMock

import pytest

from src.common.exceptions import ProfessionalPlayerNotFoundException
from src.common.schemas.riot_data_schemas import (
    PlayerMatchHistoryEntry,
    ProfessionalPlayer,
    PlayerRole,
    ProPlayerID,
    ProTeamID,
)
from src.riot.service import RiotProfessionalPlayerService

PLAYER_ID = ProPlayerID("123")


def _player():
    return ProfessionalPlayer(
        id=PLAYER_ID,
        summoner_name="Mock",
        first_name="M",
        last_name="Ock",
        image="http://x.png",
        role=PlayerRole.MID,
        team_id=ProTeamID("456"),
        team_name="Team",
        team_code="TM",
        league_name="League",
    )


def _entry(**overrides):
    base = dict(
        game_id="g",
        player_id=PLAYER_ID,
        kills=4,
        deaths=2,
        assists=6,
        total_gold=12000,
        creep_score=300,
        kill_participation=60,
        champion_damage_share=30,
        wards_placed=10,
        wards_destroyed=5,
        duration_seconds=1800,
        win=True,
        multi_kills=[],
    )
    base.update(overrides)
    return PlayerMatchHistoryEntry(**base)


def _service_with_entries(entries):
    db = MagicMock()
    db.get_player_by_id.return_value = _player()
    db.get_player_match_history.return_value = entries
    return RiotProfessionalPlayerService(db), db


def test_career_summary_no_games():
    service, _ = _service_with_entries([])
    summary = service.get_player_career_summary(PLAYER_ID)
    assert summary.games_played == 0
    assert summary.kda_ratio == 0.0
    assert summary.win_rate == 0.0


def test_career_summary_aggregates_correctly():
    entries = [
        _entry(
            game_id="g1",
            kills=2,
            deaths=1,
            assists=4,
            creep_score=270,
            total_gold=10000,
            duration_seconds=1800,  # 30 min
            win=True,
            multi_kills=["double"],
        ),
        _entry(
            game_id="g2",
            kills=6,
            deaths=3,
            assists=8,
            creep_score=360,
            total_gold=14000,
            duration_seconds=2400,  # 40 min
            win=False,
            multi_kills=["double", "triple"],
        ),
    ]
    service, _ = _service_with_entries(entries)
    summary = service.get_player_career_summary(PLAYER_ID)

    assert summary.games_played == 2
    assert summary.avg_kills == 4.0
    assert summary.avg_deaths == 2.0
    assert summary.avg_assists == 6.0
    # (2+6 + 4+8) / (1+3) = 20/4 = 5.0
    assert summary.kda_ratio == 5.0
    assert summary.avg_creep_score == 315.0
    # total cs 630 over 70 min = 9.0
    assert summary.cs_per_min == pytest.approx(9.0, abs=0.01)
    # total gold 24000 over 70 min = 342.86
    assert summary.gold_per_min == pytest.approx(342.86, abs=0.01)
    # 1 win of 2 decided = 50%
    assert summary.win_rate == 50.0
    assert summary.double_kills == 2
    assert summary.triple_kills == 1
    assert summary.quadra_kills == 0
    assert summary.penta_kills == 0


def test_career_summary_ignores_undecided_games_in_win_rate():
    entries = [_entry(win=True), _entry(win=None), _entry(win=False)]
    service, _ = _service_with_entries(entries)
    summary = service.get_player_career_summary(PLAYER_ID)
    # only 2 decided, 1 win -> 50%
    assert summary.win_rate == 50.0
    assert summary.games_played == 3


def test_match_history_validates_player_exists():
    db = MagicMock()
    db.get_player_by_id.return_value = None
    service = RiotProfessionalPlayerService(db)
    with pytest.raises(ProfessionalPlayerNotFoundException):
        service.get_player_match_history(PLAYER_ID)


def test_match_history_delegates_to_db():
    entries = [_entry(game_id="g1")]
    service, db = _service_with_entries(entries)
    result = service.get_player_match_history(PLAYER_ID)
    assert result == entries
    db.get_player_match_history.assert_called_once_with(PLAYER_ID)
