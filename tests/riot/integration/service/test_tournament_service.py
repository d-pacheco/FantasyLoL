from tests.test_base import TestBase
from tests.test_util import riot_fixtures

from src.common.schemas.riot_data_schemas import TournamentStatus, RiotTournamentID
from src.common.schemas.search_parameters import TournamentSearchParameters
from src.riot.exceptions import TournamentNotFoundException
from src.riot.service.riot_tournament_service import RiotTournamentService


class TournamentServiceTest(TestBase):
    def setUp(self):
        super().setUp()
        self.tournament_service = RiotTournamentService(self.db)

    def test_get_active_tournaments(self):
        # Arrange
        expected_tournament = riot_fixtures.active_tournament_fixture
        self.db.put_tournament(riot_fixtures.tournament_fixture)
        self.db.put_tournament(riot_fixtures.future_tournament_fixture)
        self.db.put_tournament(expected_tournament)
        search_parameters = TournamentSearchParameters(status=TournamentStatus.ACTIVE)

        # Act
        tournament_from_db = self.tournament_service.get_tournaments(search_parameters)

        # Assert
        self.assertIsInstance(tournament_from_db, list)
        self.assertEqual(len(tournament_from_db), 1)
        self.assertEqual(tournament_from_db[0], expected_tournament)

    def test_get_active_tournaments_with_no_active_tournaments(self):
        # Arrange
        self.db.put_tournament(riot_fixtures.tournament_fixture)
        self.db.put_tournament(riot_fixtures.future_tournament_fixture)
        search_parameters = TournamentSearchParameters(status=TournamentStatus.ACTIVE)

        # Act
        tournament_from_db = self.tournament_service.get_tournaments(search_parameters)

        # Assert
        self.assertIsInstance(tournament_from_db, list)
        self.assertEqual(len(tournament_from_db), 0)

    def test_get_completed_tournaments(self):
        # Arrange
        expected_tournament = riot_fixtures.tournament_fixture
        self.db.put_tournament(riot_fixtures.active_tournament_fixture)
        self.db.put_tournament(riot_fixtures.future_tournament_fixture)
        self.db.put_tournament(expected_tournament)
        search_parameters = TournamentSearchParameters(status=TournamentStatus.COMPLETED)

        # Act
        tournament_from_db = self.tournament_service.get_tournaments(search_parameters)

        # Assert
        self.assertIsInstance(tournament_from_db, list)
        self.assertEqual(len(tournament_from_db), 1)
        self.assertEqual(tournament_from_db[0], expected_tournament)

    def test_get_completed_tournaments_with_no_completed_tournaments(self):
        # Arrange
        self.db.put_tournament(riot_fixtures.active_tournament_fixture)
        self.db.put_tournament(riot_fixtures.future_tournament_fixture)
        search_parameters = TournamentSearchParameters(status=TournamentStatus.COMPLETED)

        # Act
        tournament_from_db = self.tournament_service.get_tournaments(search_parameters)

        # Assert
        self.assertIsInstance(tournament_from_db, list)
        self.assertEqual(len(tournament_from_db), 0)

    def test_get_upcoming_tournaments(self):
        # Arrange
        expected_tournament = riot_fixtures.future_tournament_fixture
        self.db.put_tournament(riot_fixtures.active_tournament_fixture)
        self.db.put_tournament(riot_fixtures.tournament_fixture)
        self.db.put_tournament(expected_tournament)
        search_parameters = TournamentSearchParameters(status=TournamentStatus.UPCOMING)

        # Act
        tournament_from_db = self.tournament_service.get_tournaments(search_parameters)

        # Assert
        self.assertIsInstance(tournament_from_db, list)
        self.assertEqual(len(tournament_from_db), 1)
        self.assertEqual(tournament_from_db[0], expected_tournament)

    def test_get_upcoming_tournaments_with_no_upcoming_tournaments(self):
        # Arrange
        self.db.put_tournament(riot_fixtures.active_tournament_fixture)
        self.db.put_tournament(riot_fixtures.tournament_fixture)
        search_parameters = TournamentSearchParameters(status=TournamentStatus.UPCOMING)

        # Act
        tournament_from_db = self.tournament_service.get_tournaments(search_parameters)

        # Assert
        self.assertIsInstance(tournament_from_db, list)
        self.assertEqual(len(tournament_from_db), 0)

    def test_get_all_tournaments(self):
        # Arrange
        self.db.put_tournament(riot_fixtures.active_tournament_fixture)
        self.db.put_tournament(riot_fixtures.tournament_fixture)
        self.db.put_tournament(riot_fixtures.future_tournament_fixture)
        search_parameters = TournamentSearchParameters()

        # Act
        tournament_from_db = self.tournament_service.get_tournaments(search_parameters)

        # Assert
        self.assertIsInstance(tournament_from_db, list)
        self.assertEqual(len(tournament_from_db), 3)

    def test_get_tournament_by_id(self):
        # Arrange
        expected_tournament = riot_fixtures.tournament_fixture
        self.db.put_tournament(expected_tournament)

        # Act
        tournament_from_db = self.tournament_service.get_tournament_by_id(expected_tournament.id)

        # Assert
        self.assertEqual(tournament_from_db, expected_tournament)

    def test_get_tournament_by_id_invalid_id(self):
        # Arrange
        self.db.put_tournament(riot_fixtures.tournament_fixture)

        # Act and Assert
        with self.assertRaises(TournamentNotFoundException):
            self.tournament_service.get_tournament_by_id(RiotTournamentID("777"))
