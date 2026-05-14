from sqlalchemy.exc import IntegrityError

from tests.test_base import TestBase
from tests.test_util import fantasy_fixtures

from src.common.schemas.fantasy_schemas import (
    FantasyLeagueID,
    FantasyLeagueStatus,
    FantasyLeagueScoringSettings,
)
from src.common.schemas.riot_data_schemas import RiotLeagueID


class TestCrudFantasyLeague(TestBase):
    def test_create_fantasy_league(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture

        # Act and Assert
        fantasy_league_before_create = self.db.get_fantasy_league_by_id(fantasy_league.id)
        self.assertIsNone(fantasy_league_before_create)
        self.db.create_fantasy_league(fantasy_league)
        fantasy_league_after_create = self.db.get_fantasy_league_by_id(fantasy_league.id)
        self.assertEqual(fantasy_league, fantasy_league_after_create)

    def test_create_fantasy_league_with_an_existing_id(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_fantasy_league(fantasy_league)

        # Act and Assert
        with self.assertRaises(IntegrityError) as context:
            self.db.create_fantasy_league(fantasy_league)
        self.assertIn("duplicate key value violates unique constraint", str(context.exception))

    def test_get_fantasy_league_by_id(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_fantasy_league(fantasy_league)

        # Act and Assert
        self.assertEqual(fantasy_league, self.db.get_fantasy_league_by_id(fantasy_league.id))
        self.assertIsNone(self.db.get_fantasy_league_by_id(FantasyLeagueID("123")))

    def test_put_fantasy_league_scoring_settings(self):
        # Arrange
        scoring_settings = fantasy_fixtures.fantasy_league_scoring_settings_fixture
        updated_scoring_settings = scoring_settings.model_copy(deep=True)
        updated_scoring_settings.kills = scoring_settings.kills + 1

        # Act and Assert
        scoring_settings_before_create = self.db.get_fantasy_league_scoring_settings_by_id(
            scoring_settings.fantasy_league_id
        )
        self.assertIsNone(scoring_settings_before_create)
        self.db.put_fantasy_league_scoring_settings(scoring_settings)
        scoring_settings_after_create = self.db.get_fantasy_league_scoring_settings_by_id(
            scoring_settings.fantasy_league_id
        )
        self.assertEqual(scoring_settings, scoring_settings_after_create)

        self.db.put_fantasy_league_scoring_settings(updated_scoring_settings)
        scoring_settings_after_update = self.db.get_fantasy_league_scoring_settings_by_id(
            scoring_settings.fantasy_league_id
        )
        self.assertEqual(updated_scoring_settings, scoring_settings_after_update)

    def test_scoring_settings_all_new_fields_round_trip(self):
        # Arrange — use non-default values to prove they're stored and retrieved
        scoring_settings = FantasyLeagueScoringSettings(
            fantasy_league_id=fantasy_fixtures.fantasy_league_fixture.id,
            kills=2,
            deaths=-1,
            assists=0.5,
            cspm=2.0,
            wards_placed=0.1,
            wards_destroyed=0.1,
            kill_participation=10,
            damage_percentage=5,
            double_kill=3.0,
            triple_kill=6.0,
            quadra_kill=12.0,
            penta_kill=25.0,
            match_win=10.0,
            match_sweep=10.0,
            dragon=2.0,
            elder_dragon=6.0,
            baron=4.0,
            tower=2.0,
            inhibitor=2.0,
            soul=8.0,
        )

        # Act
        self.db.put_fantasy_league_scoring_settings(scoring_settings)
        result = self.db.get_fantasy_league_scoring_settings_by_id(
            scoring_settings.fantasy_league_id
        )

        # Assert
        self.assertEqual(scoring_settings, result)

    def test_scoring_settings_defaults(self):
        # Arrange — create with only required field, all others should use defaults
        scoring_settings = FantasyLeagueScoringSettings(
            fantasy_league_id=fantasy_fixtures.fantasy_league_fixture.id,
        )

        # Act
        self.db.put_fantasy_league_scoring_settings(scoring_settings)
        result = self.db.get_fantasy_league_scoring_settings_by_id(
            scoring_settings.fantasy_league_id
        )

        # Assert new field defaults
        self.assertEqual(1.0, result.cspm)
        self.assertEqual(1.0, result.double_kill)
        self.assertEqual(2.0, result.triple_kill)
        self.assertEqual(4.0, result.quadra_kill)
        self.assertEqual(10.0, result.penta_kill)
        self.assertEqual(5.0, result.match_win)
        self.assertEqual(5.0, result.match_sweep)
        self.assertEqual(1.0, result.dragon)
        self.assertEqual(3.0, result.elder_dragon)
        self.assertEqual(2.0, result.baron)
        self.assertEqual(1.0, result.tower)
        self.assertEqual(1.0, result.inhibitor)
        self.assertEqual(4.0, result.soul)

    def test_get_fantasy_league_scoring_settings_by_id(self):
        # Arrange
        scoring_settings = fantasy_fixtures.fantasy_league_scoring_settings_fixture
        self.db.put_fantasy_league_scoring_settings(scoring_settings)

        # Act and Assert
        self.assertEqual(
            scoring_settings,
            self.db.get_fantasy_league_scoring_settings_by_id(scoring_settings.fantasy_league_id),
        )
        self.assertIsNone(self.db.get_fantasy_league_scoring_settings_by_id(FantasyLeagueID("123")))

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
            updated_fantasy_league_settings.number_of_teams, updated_fantasy_league.number_of_teams
        )
        self.assertNotEqual(
            updated_fantasy_league_settings.number_of_teams, fantasy_league.number_of_teams
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
            updated_fantasy_league.available_leagues,
        )
        self.assertNotEqual(
            updated_fantasy_league_settings.available_leagues, fantasy_league.available_leagues
        )
        self.assertEqual(updated_fantasy_league.name, fantasy_league.name)
        self.assertEqual(updated_fantasy_league.number_of_teams, fantasy_league.number_of_teams)

    def test_update_fantasy_league_settings_assertion_error(self):
        # Arrange
        fantasy_league_settings = fantasy_fixtures.fantasy_league_settings_fixture

        # Act and Assert
        with self.assertRaises(AssertionError):
            self.db.update_fantasy_league_settings(FantasyLeagueID("123"), fantasy_league_settings)

    def test_update_fantasy_league_status(self):
        # Arrange
        fantasy_league = fantasy_fixtures.fantasy_league_fixture
        self.db.create_fantasy_league(fantasy_league)
        new_status = FantasyLeagueStatus.DRAFT
        expected_updated_fantasy_league = fantasy_league.model_copy(deep=True)
        expected_updated_fantasy_league.status = new_status

        # Act and Assert
        self.assertNotEqual(fantasy_league.status, new_status)
        updated_fantasy_league = self.db.update_fantasy_league_status(fantasy_league.id, new_status)
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
