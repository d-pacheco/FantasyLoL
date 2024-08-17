from tests.test_base import TestBase
from tests.test_util import fantasy_fixtures

from src.common.schemas.fantasy_schemas import FantasyLeagueID, UserID
from src.common.schemas.riot_data_schemas import ProPlayerID


class TestCrudFantasyTeam(TestBase):
    def test_create_fantasy_team(self):
        # Arrange
        fantasy_team = fantasy_fixtures.fantasy_team_week_1

        # act
        self.db.put_fantasy_team(fantasy_team)

        # Assert
        users_fantasy_teams = self.db.get_all_fantasy_teams_for_user(
            fantasy_team.fantasy_league_id, user_id=fantasy_team.user_id
        )
        self.assertIsInstance(users_fantasy_teams, list)
        self.assertEqual(1, len(users_fantasy_teams))
        self.assertEqual(fantasy_team, users_fantasy_teams[0])

    def test_update_fantasy_team(self):
        # Arrange
        fantasy_team = fantasy_fixtures.fantasy_team_week_1
        self.db.put_fantasy_team(fantasy_team)
        modified_team = fantasy_team.model_copy(deep=True)
        modified_team.top_player_id = ProPlayerID("123")

        # act
        self.db.put_fantasy_team(modified_team)

        # Assert
        self.assertNotEqual(fantasy_team.top_player_id, modified_team.top_player_id)
        users_fantasy_teams = self.db.get_all_fantasy_teams_for_user(
            fantasy_team.fantasy_league_id, user_id=fantasy_team.user_id
        )
        self.assertIsInstance(users_fantasy_teams, list)
        self.assertEqual(1, len(users_fantasy_teams))
        self.assertEqual(modified_team, users_fantasy_teams[0])

    def test_get_all_fantasy_teams_for_user(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_active_fixture
        user = fantasy_fixtures.user_fixture
        fantasy_team_week_1 = fantasy_fixtures.fantasy_team_week_1
        self.db.put_fantasy_team(fantasy_team_week_1)
        fantasy_team_week_2 = fantasy_fixtures.fantasy_team_week_2
        self.db.put_fantasy_team(fantasy_team_week_2)

        # Act
        fantasy_teams_from_db = self.db.get_all_fantasy_teams_for_user(fantasy_league.id, user.id)

        # Assert
        self.assertEqual(fantasy_league.id, fantasy_team_week_1.fantasy_league_id)
        self.assertEqual(fantasy_league.id, fantasy_team_week_2.fantasy_league_id)
        self.assertIsInstance(fantasy_teams_from_db, list)
        self.assertEqual(2, len(fantasy_teams_from_db))
        fantasy_teams_from_db.sort(key=lambda x: x.week)
        self.assertEqual(fantasy_team_week_1, fantasy_teams_from_db[0])
        self.assertEqual(fantasy_team_week_2, fantasy_teams_from_db[1])

    def test_get_all_fantasy_teams_for_user_bad_fantasy_league_id(self):
        # Arrange
        user = fantasy_fixtures.user_fixture
        fantasy_team_week_1 = fantasy_fixtures.fantasy_team_week_1
        self.db.put_fantasy_team(fantasy_team_week_1)

        # Act
        fantasy_teams_from_db = self.db.get_all_fantasy_teams_for_user(
            FantasyLeagueID("badLeagueId"), user.id
        )

        # Assert
        self.assertIsInstance(fantasy_teams_from_db, list)
        self.assertEqual(0, len(fantasy_teams_from_db))

    def test_get_all_fantasy_teams_for_user_bad_user_id(self):
        # Arrange
        fantasy_team_week_1 = fantasy_fixtures.fantasy_team_week_1
        self.db.put_fantasy_team(fantasy_team_week_1)

        # Act
        fantasy_teams_from_db = self.db.get_all_fantasy_teams_for_user(
            fantasy_team_week_1.fantasy_league_id, UserID("badUserId")
        )

        # Assert
        self.assertIsInstance(fantasy_teams_from_db, list)
        self.assertEqual(0, len(fantasy_teams_from_db))

    def test_get_all_fantasy_teams_for_week(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_active_fixture
        fantasy_team_week_1 = fantasy_fixtures.fantasy_team_week_1
        self.db.put_fantasy_team(fantasy_team_week_1)
        fantasy_team_week_2 = fantasy_fixtures.fantasy_team_week_2
        self.db.put_fantasy_team(fantasy_team_week_2)

        # Act and assert
        self.assertEqual(fantasy_league.id, fantasy_team_week_1.fantasy_league_id)
        self.assertEqual(fantasy_league.id, fantasy_team_week_2.fantasy_league_id)

        week_1_fantasy_teams = self.db.get_all_fantasy_teams_for_week(fantasy_league.id, 1)
        self.assertEqual(1, len(week_1_fantasy_teams))
        self.assertEqual(fantasy_team_week_1, week_1_fantasy_teams[0])

        week_2_fantasy_teams = self.db.get_all_fantasy_teams_for_week(fantasy_league.id, 2)
        self.assertEqual(1, len(week_1_fantasy_teams))
        self.assertEqual(fantasy_team_week_2, week_2_fantasy_teams[0])

        week_3_fantasy_teams = self.db.get_all_fantasy_teams_for_week(fantasy_league.id, 3)
        self.assertEqual(0, len(week_3_fantasy_teams))
