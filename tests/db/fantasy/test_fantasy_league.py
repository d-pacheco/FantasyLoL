from sqlalchemy.exc import IntegrityError

from tests.test_base import TestBase
from tests.test_util import fantasy_fixtures

from src.common.schemas.fantasy_schemas import FantasyLeagueID, FantasyLeagueStatus
from src.common.schemas.riot_data_schemas import RiotLeagueID


class TestCrudFantasyLeague(TestBase):

    def test_create_fantasy_league(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture

        # Act and Assert
        fantasy_league_before_create = self.db.\
            get_fantasy_league_by_id(fantasy_league.id)
        self.assertIsNone(fantasy_league_before_create)
        self.db.create_fantasy_league(fantasy_league)
        fantasy_league_after_create = self.db.\
            get_fantasy_league_by_id(fantasy_league.id)
        self.assertEqual(fantasy_league, fantasy_league_after_create)

    def test_create_fantasy_league_with_an_existing_id(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_fantasy_league(fantasy_league)

        # Act and Assert
        with self.assertRaises(IntegrityError) as context:
            self.db.create_fantasy_league(fantasy_league)
        self.assertIn('UNIQUE constraint failed: fantasy_leagues.id', str(context.exception))

    def test_get_fantasy_league_by_id(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_fantasy_league(fantasy_league)

        # Act and Assert
        self.assertEqual(
            fantasy_league,
            self.db.get_fantasy_league_by_id(fantasy_league.id)
        )
        self.assertIsNone(self.db.get_fantasy_league_by_id(FantasyLeagueID("123")))

    def test_put_fantasy_league_scoring_settings(self):
        # Arrange
        scoring_settings = fantasy_fixtures.fantasy_league_scoring_settings_fixture
        updated_scoring_settings = scoring_settings.model_copy(deep=True)
        updated_scoring_settings.kills = scoring_settings.kills + 1

        # Act and Assert
        scoring_settings_before_create = self.db.\
            get_fantasy_league_scoring_settings_by_id(scoring_settings.fantasy_league_id)
        self.assertIsNone(scoring_settings_before_create)
        self.db.put_fantasy_league_scoring_settings(scoring_settings)
        scoring_settings_after_create = self.db.\
            get_fantasy_league_scoring_settings_by_id(scoring_settings.fantasy_league_id)
        self.assertEqual(scoring_settings, scoring_settings_after_create)

        self.db.put_fantasy_league_scoring_settings(updated_scoring_settings)
        scoring_settings_after_update = self.db.\
            get_fantasy_league_scoring_settings_by_id(scoring_settings.fantasy_league_id)
        self.assertEqual(updated_scoring_settings, scoring_settings_after_update)

    def test_get_fantasy_league_scoring_settings_by_id(self):
        # Arrange
        scoring_settings = fantasy_fixtures.fantasy_league_scoring_settings_fixture
        self.db.put_fantasy_league_scoring_settings(scoring_settings)

        # Act and Assert
        self.assertEqual(
            scoring_settings,
            self.db.get_fantasy_league_scoring_settings_by_id(
                scoring_settings.fantasy_league_id
            )
        )
        self.assertIsNone(
            self.db.get_fantasy_league_scoring_settings_by_id(FantasyLeagueID("123"))
        )

    def test_update_fantasy_league_settings_name(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_fantasy_league(fantasy_league)
        updated_fantasy_league_settings = fantasy_league.model_copy(deep=True)
        updated_fantasy_league_settings.name = "Updated Fantasy League name"

        # Act
        updated_fantasy_league = self.db.update_fantasy_league_settings(
            fantasy_league.id, updated_fantasy_league_settings
        )

        # Assert
        self.assertEqual(updated_fantasy_league_settings.name, updated_fantasy_league.name)
        self.assertEqual(updated_fantasy_league.number_of_teams, fantasy_league.number_of_teams)
        self.assertEqual(updated_fantasy_league.available_leagues, fantasy_league.available_leagues)
        self.assertNotEqual(updated_fantasy_league_settings.name, fantasy_league.name)

    def test_update_fantasy_league_settings_number_of_teams(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_fantasy_league(fantasy_league)
        updated_fantasy_league_settings = fantasy_league.model_copy(deep=True)
        updated_fantasy_league_settings.number_of_teams = 4

        # Act
        updated_fantasy_league = self.db.update_fantasy_league_settings(
            fantasy_league.id, updated_fantasy_league_settings
        )

        # Assert
        self.assertEqual(
            updated_fantasy_league_settings.number_of_teams,
            updated_fantasy_league.number_of_teams
        )
        self.assertNotEqual(
            updated_fantasy_league_settings.number_of_teams,
            fantasy_league.number_of_teams
        )
        self.assertEqual(updated_fantasy_league.name, fantasy_league.name)
        self.assertEqual(updated_fantasy_league.available_leagues, fantasy_league.available_leagues)

    def test_update_fantasy_league_settings_available_leagues(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_fantasy_league(fantasy_league)
        updated_fantasy_league_settings = fantasy_league.model_copy(deep=True)
        updated_fantasy_league_settings.available_leagues = [RiotLeagueID("RiotLeague1")]

        # Act
        updated_fantasy_league = self.db.update_fantasy_league_settings(
            fantasy_league.id, updated_fantasy_league_settings
        )

        # Assert
        self.assertEqual(
            updated_fantasy_league_settings.available_leagues,
            updated_fantasy_league.available_leagues
        )
        self.assertNotEqual(
            updated_fantasy_league_settings.available_leagues,
            fantasy_league.available_leagues
        )
        self.assertEqual(updated_fantasy_league.name, fantasy_league.name)
        self.assertEqual(updated_fantasy_league.number_of_teams, fantasy_league.number_of_teams)

    def test_update_fantasy_league_settings_assertion_error(self):
        # Arrange
        fantasy_league_settings = fantasy_fixtures.fantasy_league_settings_fixture

        # Act and Assert
        with self.assertRaises(AssertionError):
            self.db.update_fantasy_league_settings(
                FantasyLeagueID("123"), fantasy_league_settings
            )

    def test_update_fantasy_league_status(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_fantasy_league(fantasy_league)
        new_status = FantasyLeagueStatus.DRAFT
        expected_updated_fantasy_league = fantasy_league.model_copy(deep=True)
        expected_updated_fantasy_league.status = new_status

        # Act and Assert
        self.assertNotEqual(fantasy_league.status, new_status)
        updated_fantasy_league = self.db.update_fantasy_league_status(
            fantasy_league.id, new_status
        )
        self.assertEqual(expected_updated_fantasy_league, updated_fantasy_league)
        with self.assertRaises(AssertionError):
            self.db.update_fantasy_league_status(FantasyLeagueID("123"), new_status)

    def test_update_fantasy_league_current_draft_position(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_fantasy_league(fantasy_league)
        new_current_draft_position = 7
        expected_updated_fantasy_league = fantasy_league.model_copy(deep=True)
        expected_updated_fantasy_league.current_draft_position = new_current_draft_position

        # Act and Assert
        self.assertNotEqual(fantasy_league.current_draft_position, new_current_draft_position)
        updated_fantasy_league = self.db.update_fantasy_league_current_draft_position(
            fantasy_league.id, new_current_draft_position
        )
        self.assertEqual(expected_updated_fantasy_league, updated_fantasy_league)
        with self.assertRaises(AssertionError):
            self.db.update_fantasy_league_current_draft_position(
                FantasyLeagueID("123"), new_current_draft_position
            )
