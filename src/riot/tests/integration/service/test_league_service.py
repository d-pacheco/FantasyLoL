from src.riot.exceptions.league_not_found_exception import LeagueNotFoundException
from src.riot.service.riot_league_service import RiotLeagueService
from src.common.schemas.search_parameters import LeagueSearchParameters
from src.common.schemas import riot_data_schemas as schemas

from ...test_base import FantasyLolTestBase
from ...test_util import test_fixtures as fixtures
from ...test_util import db_util


def create_league_service():
    return RiotLeagueService()


def create_league_in_db() -> schemas.League:
    league_fixture = fixtures.league_1_fixture
    db_util.save_league(league_fixture)
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
        self.assertEqual(0, len(leagues_from_db),)

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
            league_service.get_league_by_id("777")
