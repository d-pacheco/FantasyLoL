from tests.test_base import TestBase
from tests.test_util import fantasy_fixtures

from src.common.schemas.fantasy_schemas import DraftPick, FantasyLeagueID
from src.common.schemas.riot_data_schemas import ProPlayerID, ProTeamID


class TestCrudDraftPick(TestBase):
    def test_put_and_get_draft_pick(self):
        # Arrange
        draft_pick = DraftPick(
            fantasy_league_id=fantasy_fixtures.fantasy_league_draft_fixture.id,
            pick_number=1,
            round_number=1,
            user_id=fantasy_fixtures.user_fixture.id,
            player_id=ProPlayerID("player-1"),
        )

        # Act
        self.db.put_draft_pick(draft_pick)

        # Assert
        picks = self.db.get_draft_picks_for_league(draft_pick.fantasy_league_id)
        self.assertEqual(1, len(picks))
        self.assertEqual(draft_pick, picks[0])

    def test_get_draft_picks_returns_ordered(self):
        # Arrange
        league_id = fantasy_fixtures.fantasy_league_draft_fixture.id
        pick_1 = DraftPick(
            fantasy_league_id=league_id,
            pick_number=1,
            round_number=1,
            user_id=fantasy_fixtures.user_fixture.id,
            player_id=ProPlayerID("player-1"),
        )
        pick_2 = DraftPick(
            fantasy_league_id=league_id,
            pick_number=2,
            round_number=1,
            user_id=fantasy_fixtures.user_2_fixture.id,
            team_id=ProTeamID("team-1"),
        )
        self.db.put_draft_pick(pick_2)
        self.db.put_draft_pick(pick_1)

        # Act
        picks = self.db.get_draft_picks_for_league(league_id)

        # Assert
        self.assertEqual(2, len(picks))
        self.assertEqual(pick_1, picks[0])
        self.assertEqual(pick_2, picks[1])

    def test_get_draft_picks_empty_league(self):
        # Act
        picks = self.db.get_draft_picks_for_league(FantasyLeagueID("nonexistent"))

        # Assert
        self.assertEqual([], picks)

    def test_get_draft_picks_isolated_by_league(self):
        # Arrange
        league_a = fantasy_fixtures.fantasy_league_draft_fixture.id
        league_b = fantasy_fixtures.fantasy_league_active_fixture.id
        pick_a = DraftPick(
            fantasy_league_id=league_a,
            pick_number=1,
            round_number=1,
            user_id=fantasy_fixtures.user_fixture.id,
            player_id=ProPlayerID("player-a"),
        )
        pick_b = DraftPick(
            fantasy_league_id=league_b,
            pick_number=1,
            round_number=1,
            user_id=fantasy_fixtures.user_fixture.id,
            player_id=ProPlayerID("player-b"),
        )
        self.db.put_draft_pick(pick_a)
        self.db.put_draft_pick(pick_b)

        # Act
        picks_a = self.db.get_draft_picks_for_league(league_a)
        picks_b = self.db.get_draft_picks_for_league(league_b)

        # Assert
        self.assertEqual(1, len(picks_a))
        self.assertEqual(pick_a, picks_a[0])
        self.assertEqual(1, len(picks_b))
        self.assertEqual(pick_b, picks_b[0])
