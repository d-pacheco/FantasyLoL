from copy import deepcopy
from typing import Optional

from src.common.exceptions import LeagueNotFoundException
from src.common.schemas.search_parameters import LeagueSearchParameters
from src.common.schemas.riot_data_schemas import League, RiotLeagueID
from src.db import crud
from src.riot.service import RiotLeagueService

from tests.test_base import FantasyLolTestBase
from tests.test_util import riot_fixtures as fixtures


def create_league_service():
    return RiotLeagueService()


def create_league_in_db(league_fixture: Optional[League] = None) -> League:
    if league_fixture is None:
        league_fixture = fixtures.league_1_fixture
    crud.put_league(league_fixture)
    return league_fixture


class LeagueServiceTest(FantasyLolTestBase):

    def test_get_leagues_by_name_existing_league(self):
        # Arrange
        league_fixture = create_league_in_db()
        league_service = create_league_service()
        search_parameters = LeagueSearchParameters(name=league_fixture.name)

        # Act
        leagues_from_db = league_service.get_leagues(search_parameters)

        # Assert
        self.assertIsInstance(leagues_from_db, list)
        self.assertEqual(1, len(leagues_from_db))
        self.assertEqual(league_fixture, leagues_from_db[0])

    def test_get_leagues_by_name_no_existing_league(self):
        # Arrange
        create_league_in_db()
        league_service = create_league_service()
        search_parameters = LeagueSearchParameters(name="badName")

        # Act
        leagues_from_db = league_service.get_leagues(search_parameters)

        # Assert
        self.assertIsInstance(leagues_from_db, list)
        self.assertEqual(0, len(leagues_from_db), )

    def test_get_leagues_by_region_existing_league(self):
        # Arrange
        league_fixture = create_league_in_db()
        league_service = create_league_service()
        search_parameters = LeagueSearchParameters(region=league_fixture.region)

        # Act
        leagues_from_db = league_service.get_leagues(search_parameters)

        # Assert
        self.assertIsInstance(leagues_from_db, list)
        self.assertEqual(1, len(leagues_from_db))
        self.assertEqual(league_fixture, leagues_from_db[0])

    def test_get_leagues_by_region_no_existing_league(self):
        # Arrange
        league_service = create_league_service()
        search_parameters = LeagueSearchParameters(region="badRegion")

        # Act
        leagues_from_db = league_service.get_leagues(search_parameters)

        # Assert
        self.assertIsInstance(leagues_from_db, list)
        self.assertEqual(0, len(leagues_from_db))

    def test_get_leagues_by_fantasy_available_false_existing_league(self):
        # Arrange
        league_service = create_league_service()
        league_fixture_not_available = create_league_in_db(fixtures.league_1_fixture)
        league_fixture_available = create_league_in_db(fixtures.league_2_fixture)
        search_parameters = LeagueSearchParameters(
            fantasy_available=league_fixture_not_available.fantasy_available
        )

        # Act
        leagues_from_db = league_service.get_leagues(search_parameters)

        # Assert
        self.assertEqual(False, league_fixture_not_available.fantasy_available)
        self.assertEqual(True, league_fixture_available.fantasy_available)
        self.assertIsInstance(leagues_from_db, list)
        self.assertEqual(1, len(leagues_from_db))
        self.assertEqual(league_fixture_not_available, leagues_from_db[0])

    def test_get_leagues_by_fantasy_available_true_existing_league(self):
        # Arrange
        league_service = create_league_service()
        league_fixture_not_available = create_league_in_db(fixtures.league_1_fixture)
        league_fixture_available = create_league_in_db(fixtures.league_2_fixture)
        search_parameters = LeagueSearchParameters(
            fantasy_available=league_fixture_available.fantasy_available
        )

        # Act
        leagues_from_db = league_service.get_leagues(search_parameters)

        # Assert
        self.assertEqual(False, league_fixture_not_available.fantasy_available)
        self.assertEqual(True, league_fixture_available.fantasy_available)
        self.assertIsInstance(leagues_from_db, list)
        self.assertEqual(1, len(leagues_from_db))
        self.assertEqual(league_fixture_available, leagues_from_db[0])

    def test_get_leagues_empty_query_params(self):
        # Arrange
        league_fixture = create_league_in_db()
        league_service = create_league_service()
        search_parameters = LeagueSearchParameters()

        # Act
        leagues_from_db = league_service.get_leagues(search_parameters)

        # Assert
        self.assertIsInstance(leagues_from_db, list)
        self.assertEqual(1, len(leagues_from_db))
        self.assertEqual(league_fixture, leagues_from_db[0])

    def test_get_league_by_id_valid_id(self):
        # Arrange
        league_fixture = create_league_in_db()
        league_service = create_league_service()

        # Act
        league_from_db = league_service.get_league_by_id(league_fixture.id)

        # Assert
        self.assertEqual(league_fixture, league_from_db)

    def test_get_league_by_id_invalid_id(self):
        # Arrange
        create_league_in_db()
        league_service = create_league_service()

        # Act and Assert
        with self.assertRaises(LeagueNotFoundException):
            league_service.get_league_by_id(RiotLeagueID("777"))

    def test_update_fantasy_available_to_true(self):
        # Arrange
        league_service = create_league_service()
        fantasy_league = fixtures.league_1_fixture
        create_league_in_db(fantasy_league)
        new_status = True
        expected_updated_league = deepcopy(fantasy_league)
        expected_updated_league.fantasy_available = new_status

        # Act
        updated_league = league_service.update_fantasy_available(fantasy_league.id, new_status)

        # Assert
        self.assertEqual(expected_updated_league, updated_league)
        self.assertNotEqual(
            expected_updated_league.fantasy_available,
            fantasy_league.fantasy_available
        )

    def test_update_fantasy_available_to_false(self):
        # Arrange
        league_service = create_league_service()
        fantasy_league = fixtures.league_2_fixture
        create_league_in_db(fantasy_league)
        new_status = False
        expected_updated_league = deepcopy(fantasy_league)
        expected_updated_league.fantasy_available = new_status

        # Act
        updated_league = league_service.update_fantasy_available(fantasy_league.id, new_status)

        # Assert
        self.assertEqual(expected_updated_league, updated_league)
        self.assertNotEqual(
            expected_updated_league.fantasy_available,
            fantasy_league.fantasy_available
        )

    def test_update_fantasy_available_non_existing_league_exception(self):
        # Arrange
        league_service = create_league_service()
        fantasy_league = fixtures.league_1_fixture
        create_league_in_db(fantasy_league)
        new_status = True

        # Act and Assert
        with self.assertRaises(LeagueNotFoundException):
            league_service.update_fantasy_available(RiotLeagueID("badId"), new_status)
