from src.riot.exceptions import MatchNotFoundException
from src.riot.service import RiotMatchService
from src.common.schemas.search_parameters import MatchSearchParameters
from src.common.schemas.riot_data_schemas import RiotMatchID

from tests.test_base import FantasyLolTestBase
from tests.test_util import riot_data_util


def create_match_service():
    return RiotMatchService()


class MatchServiceTest(FantasyLolTestBase):
    def test_get_matches_by_league_slug_existing_match(self):
        # Arrange
        expected_match = riot_data_util.create_match_in_db()
        match_service = create_match_service()
        search_parameters = MatchSearchParameters(league_slug=expected_match.league_slug)

        # Act
        matches_from_db = match_service.get_matches(search_parameters)

        # Assert
        self.assertIsInstance(matches_from_db, list)
        self.assertEqual(1, len(matches_from_db))
        self.assertEqual(expected_match, matches_from_db[0])

    def test_get_matches_by_league_slug_no_existing_match(self):
        # Arrange
        riot_data_util.create_match_in_db()
        match_service = create_match_service()
        search_parameters = MatchSearchParameters(league_slug="bad-slug")

        # Act
        matches_from_db = match_service.get_matches(search_parameters)

        # Assert
        self.assertIsInstance(matches_from_db, list)
        self.assertEqual(0, len(matches_from_db))

    def test_get_matches_by_tournament_id_existing_match(self):
        # Arrange
        expected_match = riot_data_util.create_match_in_db()
        match_service = create_match_service()
        search_parameters = MatchSearchParameters(tournament_id=expected_match.tournament_id)

        # Act
        matches_from_db = match_service.get_matches(search_parameters)

        # Assert
        self.assertIsInstance(matches_from_db, list)
        self.assertEqual(1, len(matches_from_db))
        self.assertEqual(expected_match, matches_from_db[0])

    def test_get_matches_by_tournament_id_no_existing_match(self):
        # Arrange
        riot_data_util.create_match_in_db()
        match_service = create_match_service()
        search_parameters = MatchSearchParameters(tournament_id="777")

        # Act
        matches_from_db = match_service.get_matches(search_parameters)

        # Assert
        self.assertIsInstance(matches_from_db, list)
        self.assertEqual(0, len(matches_from_db))

    def test_get_matches_with_empty_query_params(self):
        # Arrange
        expected_match = riot_data_util.create_match_in_db()
        match_service = create_match_service()
        search_parameters = MatchSearchParameters()

        # Act
        matches_from_db = match_service.get_matches(search_parameters)

        # Assert
        self.assertIsInstance(matches_from_db, list)
        self.assertEqual(1, len(matches_from_db))
        self.assertEqual(expected_match, matches_from_db[0])

    def test_get_matches_by_id_with_valid_id(self):
        # Arrange
        expected_match = riot_data_util.create_match_in_db()
        match_service = create_match_service()

        # Act
        match_from_db = match_service.get_match_by_id(expected_match.id)

        # Assert
        self.assertEqual(expected_match, match_from_db)

    def test_get_matches_by_id_with_invalid_id(self):
        # Arrange
        riot_data_util.create_match_in_db()
        match_service = create_match_service()

        # Act and Assert
        with self.assertRaises(MatchNotFoundException):
            match_service.get_match_by_id(RiotMatchID("777"))
