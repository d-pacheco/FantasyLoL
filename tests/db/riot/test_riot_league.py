from tests.test_base import TestBase
from tests.test_util import riot_fixtures

from src.db.models import LeagueModel
from src.common.schemas.riot_data_schemas import RiotLeagueID, League, ProPlayerID


class TestCrudRiotLeague(TestBase):
    def test_put_league_no_existing_league(self):
        # Arrange
        league = riot_fixtures.league_1_fixture

        # Act and Assert
        league_before_put = self.db.get_league_by_id(league.id)
        self.assertIsNone(league_before_put)
        self.db.put_league(league)
        league_after_put = self.db.get_league_by_id(league.id)
        self.assertEqual(league, league_after_put)

    def test_put_league_existing_league(self):
        # Arrange
        league = riot_fixtures.league_1_fixture
        self.db.put_league(league)
        updated_league = league.model_copy(deep=True)
        updated_league.priority = league.priority + 1

        # Act and Assert
        league_before_put = self.db.get_league_by_id(league.id)
        self.assertEqual(league, league_before_put)
        self.assertEqual(league.id, updated_league.id)
        self.db.put_league(updated_league)
        league_after_put = self.db.get_league_by_id(league.id)
        self.assertEqual(updated_league, league_after_put)

    def test_get_leagues_no_filters(self):
        # Arrange
        expected_league = riot_fixtures.league_1_fixture
        self.db.put_league(expected_league)

        # Act
        leagues_from_db = self.db.get_leagues()

        # Assert
        self.assertIsInstance(leagues_from_db, list)
        self.assertEqual(1, len(leagues_from_db))
        league_from_db = leagues_from_db[0]
        self.assertIsInstance(league_from_db, League)
        self.assertEqual(expected_league, leagues_from_db[0])

    def test_get_leagues_empty_filters(self):
        # Arrange
        filters = []
        expected_league = riot_fixtures.league_1_fixture
        self.db.put_league(expected_league)

        # Act
        leagues_from_db = self.db.get_leagues(filters)

        # Assert
        self.assertIsInstance(leagues_from_db, list)
        self.assertEqual(1, len(leagues_from_db))
        league_from_db = leagues_from_db[0]
        self.assertIsInstance(league_from_db, League)
        self.assertEqual(expected_league, league_from_db)

    def test_get_leagues_name_filter(self):
        # Arrange
        filters = []
        expected_league = riot_fixtures.league_1_fixture
        filters.append(LeagueModel.name == expected_league.name)
        self.db.put_league(expected_league)
        self.db.put_league(riot_fixtures.league_2_fixture)

        # Act
        leagues_from_db = self.db.get_leagues(filters)

        # Assert
        self.assertIsInstance(leagues_from_db, list)
        self.assertEqual(1, len(leagues_from_db))
        league_from_db = leagues_from_db[0]
        self.assertIsInstance(league_from_db, League)
        self.assertEqual(expected_league, league_from_db)

    def test_get_leagues_name_filter_no_league(self):
        # Arrange
        filters = []
        expected_league = riot_fixtures.league_1_fixture
        filters.append(LeagueModel.name == expected_league.name)
        self.db.put_league(riot_fixtures.league_2_fixture)

        # Act
        leagues_from_db = self.db.get_leagues(filters)

        # Assert
        self.assertIsInstance(leagues_from_db, list)
        self.assertEqual(0, len(leagues_from_db))

    def test_get_leagues_region_filter(self):
        # Arrange
        filters = []
        expected_league = riot_fixtures.league_1_fixture
        filters.append(LeagueModel.region == expected_league.region)
        self.db.put_league(expected_league)
        self.db.put_league(riot_fixtures.league_2_fixture)

        # Act
        leagues_from_db = self.db.get_leagues(filters)

        # Assert
        self.assertIsInstance(leagues_from_db, list)
        self.assertEqual(1, len(leagues_from_db))
        league_from_db = leagues_from_db[0]
        self.assertIsInstance(league_from_db, League)
        self.assertEqual(expected_league, league_from_db)

    def test_get_leagues_region_filter_no_league(self):
        # Arrange
        filters = []
        expected_league = riot_fixtures.league_1_fixture
        filters.append(LeagueModel.region == expected_league.region)
        self.db.put_league(riot_fixtures.league_2_fixture)

        # Act
        leagues_from_db = self.db.get_leagues(filters)

        # Assert
        self.assertIsInstance(leagues_from_db, list)
        self.assertEqual(0, len(leagues_from_db))

    def test_get_league_by_id_existing_league(self):
        # Arrange
        expected_league = riot_fixtures.league_1_fixture
        self.db.put_league(expected_league)

        # Act
        league_from_db = self.db.get_league_by_id(expected_league.id)

        # Assert
        self.assertIsNotNone(league_from_db)
        self.assertIsInstance(league_from_db, League)
        self.assertEqual(expected_league, league_from_db)

    def test_get_league_by_id_no_existing_league(self):
        # Arrange
        expected_league = riot_fixtures.league_1_fixture

        # Act
        league_from_db = self.db.get_league_by_id(expected_league.id)

        # Assert
        self.assertIsNone(league_from_db)

    def test_update_league_fantasy_available_status_existing_league(self):
        # Arrange
        league = riot_fixtures.league_1_fixture
        self.db.put_league(league)
        new_status = not league.fantasy_available
        expected_updated_league = league.model_copy(deep=True)
        expected_updated_league.fantasy_available = new_status

        # Act
        updated_league = self.db.update_league_fantasy_available_status(league.id, new_status)

        # Assert
        self.assertNotEqual(new_status, league.fantasy_available)
        self.assertEqual(expected_updated_league, updated_league)
        league_from_db = self.db.get_league_by_id(league.id)
        self.assertEqual(expected_updated_league, league_from_db)

    def test_update_league_fantasy_available_status_no_existing_league(self):
        # Arrange
        league = riot_fixtures.league_1_fixture
        self.db.put_league(league)
        new_status = not league.fantasy_available

        # Act
        updated_league = self.db.update_league_fantasy_available_status(
            RiotLeagueID("badLeagueId"), new_status
        )

        # Assert
        self.assertNotEqual(new_status, league.fantasy_available)
        self.assertIsNone(updated_league)

    def test_get_league_ids_for_player_successful(self):
        # Arrange
        self.db.put_league(riot_fixtures.league_1_fixture)
        self.db.put_league(riot_fixtures.league_2_fixture)
        self.db.put_team(riot_fixtures.team_1_fixture)
        self.db.put_team(riot_fixtures.team_2_fixture)
        self.db.put_player(riot_fixtures.player_1_fixture)

        # Act
        league_ids = self.db.get_league_ids_for_player(riot_fixtures.player_1_fixture.id)

        # Assert
        self.assertIsInstance(league_ids, list)
        self.assertEqual(1, len(league_ids))
        self.assertEqual(riot_fixtures.league_1_fixture.id, league_ids[0])

    def test_get_league_ids_for_player_non_existing_player_id(self):
        # Arrange
        self.db.put_league(riot_fixtures.league_1_fixture)
        self.db.put_league(riot_fixtures.league_2_fixture)
        self.db.put_team(riot_fixtures.team_1_fixture)
        self.db.put_team(riot_fixtures.team_2_fixture)
        self.db.put_player(riot_fixtures.player_1_fixture)

        # Act
        league_ids = self.db.get_league_ids_for_player(ProPlayerID("123"))

        # Assert
        self.assertIsInstance(league_ids, list)
        self.assertEqual(0, len(league_ids))
