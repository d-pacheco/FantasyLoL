"""Unit tests for team detail service logic (mocked DatabaseService)."""

from unittest.mock import MagicMock

import pytest

from src.common.schemas.riot_data_schemas import (
    ProfessionalPlayer,
    ProfessionalTeam,
    PlayerRole,
    ProPlayerID,
    ProTeamID,
    TeamMatchHistoryEntry,
)
from src.riot.exceptions import ProfessionalTeamNotFoundException
from src.riot.service import RiotProfessionalTeamService

TEAM_ID = ProTeamID("456")


def _team():
    return ProfessionalTeam(
        id=TEAM_ID,
        slug="home",
        name="Home",
        code="HOME",
        image="http://h.png",
        alternative_image=None,
        background_image=None,
        status="active",
        home_league_name="League",
        home_league_region="MOCK",
    )


def _player(name, role):
    return ProfessionalPlayer(
        id=ProPlayerID(name),
        summoner_name=name,
        first_name="",
        last_name="",
        image="",
        role=role,
        team_id=TEAM_ID,
        team_name="Home",
        team_code="HOME",
        league_name="League",
    )


def _service(db):
    return RiotProfessionalTeamService(db)


def test_get_team_roster_orders_by_role():
    db = MagicMock()
    db.get_team_by_id.return_value = _team()
    # deliberately unsorted, with a sub sharing the mid role
    db.get_players.return_value = [
        _player("SupPlayer", PlayerRole.SUPPORT),
        _player("TopPlayer", PlayerRole.TOP),
        _player("MidSub", PlayerRole.MID),
        _player("AdcPlayer", PlayerRole.BOTTOM),
        _player("JnglPlayer", PlayerRole.JUNGLE),
        _player("MidPlayer", PlayerRole.MID),
    ]
    roster = _service(db).get_team_roster(TEAM_ID)
    roles = [p.role for p in roster]
    assert roles == [
        PlayerRole.TOP,
        PlayerRole.JUNGLE,
        PlayerRole.MID,
        PlayerRole.MID,
        PlayerRole.BOTTOM,
        PlayerRole.SUPPORT,
    ]


def test_get_team_roster_not_found():
    db = MagicMock()
    db.get_team_by_id.return_value = None
    with pytest.raises(ProfessionalTeamNotFoundException):
        _service(db).get_team_roster(TEAM_ID)


def _match(win):
    return TeamMatchHistoryEntry(match_id="m", win=win)


def test_get_team_summary_aggregates():
    db = MagicMock()
    db.get_team_by_id.return_value = _team()
    db.get_team_match_history.return_value = [
        _match(True),
        _match(True),
        _match(False),
        _match(None),
    ]
    db.get_team_game_stat_lines.return_value = [
        {
            "total_kills": 15,
            "total_gold": 60000,
            "towers": 8,
            "barons": 1,
            "inhibitors": 1,
            "dragons": 3,
        },
        {
            "total_kills": 10,
            "total_gold": 50000,
            "towers": 6,
            "barons": 0,
            "inhibitors": 1,
            "dragons": 1,
        },
    ]
    summary = _service(db).get_team_summary(TEAM_ID)

    assert summary.matches_played == 4
    assert summary.wins == 2
    assert summary.losses == 1
    # 2 wins of 3 decided => 66.67
    assert summary.win_rate == pytest.approx(66.67, abs=0.01)
    assert summary.games_counted == 2
    assert summary.avg_kills == 12.5
    assert summary.avg_gold == 55000.0
    assert summary.avg_towers == 7.0
    assert summary.avg_barons == 0.5
    assert summary.avg_inhibitors == 1.0
    assert summary.avg_dragons == 2.0


def test_get_team_summary_no_games():
    db = MagicMock()
    db.get_team_by_id.return_value = _team()
    db.get_team_match_history.return_value = []
    db.get_team_game_stat_lines.return_value = []
    summary = _service(db).get_team_summary(TEAM_ID)
    assert summary.matches_played == 0
    assert summary.win_rate == 0.0
    assert summary.avg_kills == 0.0


def test_get_team_match_history_delegates():
    db = MagicMock()
    db.get_team_by_id.return_value = _team()
    entries = [_match(True)]
    db.get_team_match_history.return_value = entries
    result = _service(db).get_team_match_history(TEAM_ID)
    assert result == entries
    db.get_team_match_history.assert_called_once_with(TEAM_ID)
