from datetime import datetime

from tests.test_base import FantasyLolTestBase
from tests.test_util import riot_fixtures

from src.db import crud
from src.db.models import TournamentModel

from src.common.schemas.riot_data_schemas import Tournament


class TestCrudRiotTournament(FantasyLolTestBase):
    def test_put_tournament_no_existing_tournament(self):
        # Arrange
        tournament = riot_fixtures.tournament_fixture

        # Act and Assert
        tournament_before_put = crud.get_tournament_by_id(tournament.id)
        self.assertIsNone(tournament_before_put)
        crud.put_tournament(tournament)
        tournament_after_put = crud.get_tournament_by_id(tournament.id)
        self.assertEqual(tournament, tournament_after_put)

    def test_put_tournament_existing_tournament(self):
        # Arrange
        tournament = riot_fixtures.tournament_fixture
        crud.put_tournament(tournament)
        updated_tournament = tournament.model_copy(deep=True)
        updated_tournament.end_date = "2070-02-03"

        # Act and Assert
        tournament_before_put = crud.get_tournament_by_id(tournament.id)
        self.assertEqual(tournament_before_put, tournament)
        crud.put_tournament(updated_tournament)
        self.assertEqual(tournament.id, updated_tournament.id)
        tournament_after_put = crud.get_tournament_by_id(tournament.id)
        self.assertEqual(updated_tournament, tournament_after_put)

    def test_get_tournaments_empty_filters_existing_tournaments(self):
        # Arrange
        filters = []
        expected_tournament = riot_fixtures.tournament_fixture
        crud.put_tournament(expected_tournament)

        # Act
        tournaments_from_db = crud.get_tournaments(filters)

        # Assert
        self.assertIsInstance(tournaments_from_db, list)
        self.assertEqual(1, len(tournaments_from_db))
        tournament_from_db = tournaments_from_db[0]
        self.assertIsInstance(tournament_from_db, Tournament)
        self.assertEqual(expected_tournament, tournament_from_db)

    def test_get_tournaments_empty_filters_no_existing_tournaments(self):
        # Arrange
        filters = []

        # Act
        tournaments_from_db = crud.get_tournaments(filters)

        # Assert
        self.assertIsInstance(tournaments_from_db, list)
        self.assertEqual(0, len(tournaments_from_db))

    def test_get_tournaments_start_date_filter_existing_tournament(self):
        # Arrange
        current_date = datetime.now()
        filters = [TournamentModel.start_date < current_date]
        expected_tournament = riot_fixtures.tournament_fixture
        crud.put_tournament(expected_tournament)

        # Act
        tournaments_from_db = crud.get_tournaments(filters)

        # Assert
        self.assertIsInstance(tournaments_from_db, list)
        self.assertEqual(1, len(tournaments_from_db))
        tournament_from_db = tournaments_from_db[0]
        self.assertIsInstance(tournament_from_db, Tournament)
        self.assertEqual(expected_tournament, tournament_from_db)

    def test_get_tournaments_start_date_filter_no_existing_tournament(self):
        # Arrange
        current_date = datetime.now()
        filters = [TournamentModel.start_date > current_date]
        expected_tournament = riot_fixtures.tournament_fixture
        crud.put_tournament(expected_tournament)

        # Act
        tournaments_from_db = crud.get_tournaments(filters)

        # Assert
        self.assertIsInstance(tournaments_from_db, list)
        self.assertEqual(0, len(tournaments_from_db))

    def test_get_tournaments_end_date_filter_existing_tournament(self):
        # Arrange
        current_date = datetime.now()
        filters = [TournamentModel.end_date < current_date]
        expected_tournament = riot_fixtures.tournament_fixture
        crud.put_tournament(expected_tournament)

        # Act
        tournaments_from_db = crud.get_tournaments(filters)

        # Assert
        self.assertIsInstance(tournaments_from_db, list)
        self.assertEqual(1, len(tournaments_from_db))
        tournament_from_db = tournaments_from_db[0]
        self.assertIsInstance(tournament_from_db, Tournament)
        self.assertEqual(expected_tournament, tournament_from_db)

    def test_get_tournaments_end_date_filter_no_existing_tournament(self):
        # Arrange
        current_date = datetime.now()
        filters = [TournamentModel.end_date > current_date]
        expected_tournament = riot_fixtures.tournament_fixture
        crud.put_tournament(expected_tournament)

        # Act
        tournaments_from_db = crud.get_tournaments(filters)

        # Assert
        self.assertIsInstance(tournaments_from_db, list)
        self.assertEqual(0, len(tournaments_from_db))

    def test_get_tournament_by_id_existing_tournament(self):
        # Arrange
        expected_tournament = riot_fixtures.tournament_fixture
        crud.put_tournament(expected_tournament)

        # Act
        tournament_from_db = crud.get_tournament_by_id(expected_tournament.id)

        # Assert
        self.assertIsNotNone(tournament_from_db)
        self.assertIsInstance(tournament_from_db, Tournament)
        self.assertEqual(expected_tournament, tournament_from_db)

    def test_get_tournament_by_id_no_existing_tournament(self):
        # Arrange
        expected_tournament = riot_fixtures.tournament_fixture

        # Act
        tournament_from_db = crud.get_tournament_by_id(expected_tournament.id)

        # Assert
        self.assertIsNone(tournament_from_db)
