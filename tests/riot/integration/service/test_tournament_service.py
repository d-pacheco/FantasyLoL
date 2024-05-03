from tests.test_base import FantasyLolTestBase
from tests.test_util import riot_data_util

from src.riot.exceptions.tournament_not_found_exception import TournamentNotFoundException
from src.riot.service.riot_tournament_service import RiotTournamentService
from src.common.schemas.riot_data_schemas import TournamentStatus
from src.common.schemas.search_parameters import TournamentSearchParameters


def create_tournament_service():
    return RiotTournamentService()


class TournamentServiceTest(FantasyLolTestBase):
    def test_get_active_tournaments(self):
        # Arrange
        tournament_service = create_tournament_service()
        riot_data_util.create_completed_tournament_in_db()
        riot_data_util.create_upcoming_tournament_in_db()
        expected_tournament = riot_data_util.create_active_tournament_in_db()
        search_parameters = TournamentSearchParameters(status=TournamentStatus.ACTIVE)

        # Act
        tournament_from_db = tournament_service.get_tournaments(search_parameters)

        # Assert
        self.assertIsInstance(tournament_from_db, list)
        self.assertEqual(len(tournament_from_db), 1)
        self.assertEqual(tournament_from_db[0], expected_tournament)

    def test_get_active_tournaments_with_no_active_tournaments(self):
        # Arrange
        tournament_service = create_tournament_service()
        riot_data_util.create_completed_tournament_in_db()
        riot_data_util.create_upcoming_tournament_in_db()
        search_parameters = TournamentSearchParameters(status=TournamentStatus.ACTIVE)

        # Act
        tournament_from_db = tournament_service.get_tournaments(search_parameters)

        # Assert
        self.assertIsInstance(tournament_from_db, list)
        self.assertEqual(len(tournament_from_db), 0)

    def test_get_completed_tournaments(self):
        # Arrange
        tournament_service = create_tournament_service()
        riot_data_util.create_active_tournament_in_db()
        riot_data_util.create_upcoming_tournament_in_db()
        expected_tournament = riot_data_util.create_completed_tournament_in_db()
        search_parameters = TournamentSearchParameters(status=TournamentStatus.COMPLETED)

        # Act
        tournament_from_db = tournament_service.get_tournaments(search_parameters)

        # Assert
        self.assertIsInstance(tournament_from_db, list)
        self.assertEqual(len(tournament_from_db), 1)
        self.assertEqual(tournament_from_db[0], expected_tournament)

    def test_get_completed_tournaments_with_no_completed_tournaments(self):
        # Arrange
        tournament_service = create_tournament_service()
        riot_data_util.create_active_tournament_in_db()
        riot_data_util.create_upcoming_tournament_in_db()
        search_parameters = TournamentSearchParameters(status=TournamentStatus.COMPLETED)

        # Act
        tournament_from_db = tournament_service.get_tournaments(search_parameters)

        # Assert
        self.assertIsInstance(tournament_from_db, list)
        self.assertEqual(len(tournament_from_db), 0)

    def test_get_upcoming_tournaments(self):
        # Arrange
        tournament_service = create_tournament_service()
        riot_data_util.create_active_tournament_in_db()
        riot_data_util.create_completed_tournament_in_db()
        expected_tournament = riot_data_util.create_upcoming_tournament_in_db()
        search_parameters = TournamentSearchParameters(status=TournamentStatus.UPCOMING)

        # Act
        tournament_from_db = tournament_service.get_tournaments(search_parameters)

        # Assert
        self.assertIsInstance(tournament_from_db, list)
        self.assertEqual(len(tournament_from_db), 1)
        self.assertEqual(tournament_from_db[0], expected_tournament)

    def test_get_upcoming_tournaments_with_no_upcoming_tournaments(self):
        # Arrange
        tournament_service = create_tournament_service()
        riot_data_util.create_active_tournament_in_db()
        riot_data_util.create_completed_tournament_in_db()
        search_parameters = TournamentSearchParameters(status=TournamentStatus.UPCOMING)

        # Act
        tournament_from_db = tournament_service.get_tournaments(search_parameters)

        # Assert
        self.assertIsInstance(tournament_from_db, list)
        self.assertEqual(len(tournament_from_db), 0)

    def test_get_all_tournaments(self):
        # Arrange
        tournament_service = create_tournament_service()
        riot_data_util.create_active_tournament_in_db()
        riot_data_util.create_completed_tournament_in_db()
        riot_data_util.create_upcoming_tournament_in_db()
        search_parameters = TournamentSearchParameters()

        # Act
        tournament_from_db = tournament_service.get_tournaments(search_parameters)

        # Assert
        self.assertIsInstance(tournament_from_db, list)
        self.assertEqual(len(tournament_from_db), 3)

    def test_get_tournament_by_id(self):
        # Arrange
        tournament_service = create_tournament_service()
        expected_tournament = riot_data_util.create_completed_tournament_in_db()

        # Act
        tournament_from_db = tournament_service.get_tournament_by_id(expected_tournament.id)

        # Assert
        self.assertEqual(tournament_from_db, expected_tournament)

    def test_get_tournament_by_id_invalid_id(self):
        # Arrange
        tournament_service = create_tournament_service()
        riot_data_util.create_completed_tournament_in_db()

        # Act and Assert
        with self.assertRaises(TournamentNotFoundException):
            tournament_service.get_tournament_by_id("777")
