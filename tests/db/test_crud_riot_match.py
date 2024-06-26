from src.common.schemas.riot_data_schemas import Match, RiotMatchID
from src.db import crud
from src.db.models import MatchModel
from tests.test_base import FantasyLolTestBase
from tests.test_util import riot_fixtures


class TestCrudRiotMatch(FantasyLolTestBase):
    def test_put_match_no_existing_match(self):
        # Arrange
        match = riot_fixtures.match_fixture

        # Act and Assert
        match_before_put = crud.get_match_by_id(match.id)
        self.assertIsNone(match_before_put)
        crud.put_match(match)
        match_after_put = crud.get_match_by_id(match.id)
        self.assertEqual(match, match_after_put)

    def test_put_match_existing_match(self):
        # Arrange
        match = riot_fixtures.match_fixture
        crud.put_match(match)
        updated_match = match.model_copy(deep=True)
        updated_match.strategy_count = match.strategy_count + 2

        # Act and Assert
        match_before_put = crud.get_match_by_id(match.id)
        self.assertEqual(match, match_before_put)
        self.assertEqual(match.id, updated_match.id)
        crud.put_match(updated_match)
        match_after_put = crud.get_match_by_id(match.id)
        self.assertEqual(updated_match, match_after_put)

    def test_get_matches_no_filters(self):
        # Arrange
        expected_match = riot_fixtures.match_fixture
        crud.put_match(expected_match)

        # Act
        matches_from_db = crud.get_matches()

        # Assert
        self.assertIsInstance(matches_from_db, list)
        self.assertEqual(1, len(matches_from_db))
        match_from_db = matches_from_db[0]
        self.assertIsInstance(match_from_db, Match)
        self.assertEqual(expected_match, match_from_db)

    def test_get_matches_empty_filters(self):
        # Arrange
        filters = []
        expected_match = riot_fixtures.match_fixture
        crud.put_match(expected_match)

        # Act
        matches_from_db = crud.get_matches(filters)

        # Assert
        self.assertIsInstance(matches_from_db, list)
        self.assertEqual(1, len(matches_from_db))
        match_from_db = matches_from_db[0]
        self.assertIsInstance(match_from_db, Match)
        self.assertEqual(expected_match, match_from_db)

    def test_get_matches_league_slug_filter_existing_match(self):
        # Arrange
        filters = []
        expected_match = riot_fixtures.match_fixture
        filters.append(MatchModel.league_slug == expected_match.league_slug)
        crud.put_match(expected_match)

        # Act
        matches_from_db = crud.get_matches(filters)

        # Assert
        self.assertIsInstance(matches_from_db, list)
        self.assertEqual(1, len(matches_from_db))
        match_from_db = matches_from_db[0]
        self.assertIsInstance(match_from_db, Match)
        self.assertEqual(expected_match, match_from_db)

    def test_get_matches_league_slug_filter_no_existing_match(self):
        # Arrange
        filters = []
        expected_match = riot_fixtures.match_fixture
        filters.append(MatchModel.league_slug == "badFilter")
        crud.put_match(expected_match)

        # Act
        matches_from_db = crud.get_matches(filters)

        # Assert
        self.assertIsInstance(matches_from_db, list)
        self.assertEqual(0, len(matches_from_db))

    def test_get_matches_tournament_id_filter_existing_match(self):
        # Arrange
        filters = []
        expected_match = riot_fixtures.match_fixture
        filters.append(MatchModel.tournament_id == expected_match.tournament_id)
        crud.put_match(expected_match)

        # Act
        matches_from_db = crud.get_matches(filters)

        # Assert
        self.assertIsInstance(matches_from_db, list)
        self.assertEqual(1, len(matches_from_db))
        match_from_db = matches_from_db[0]
        self.assertIsInstance(match_from_db, Match)
        self.assertEqual(expected_match, match_from_db)

    def test_get_matches_tournament_id_filter_no_existing_match(self):
        # Arrange
        filters = []
        expected_match = riot_fixtures.match_fixture
        filters.append(MatchModel.tournament_id == "badFilter")
        crud.put_match(expected_match)

        # Act
        matches_from_db = crud.get_matches(filters)

        # Assert
        self.assertIsInstance(matches_from_db, list)
        self.assertEqual(0, len(matches_from_db))

    def test_get_match_by_id_existing_match(self):
        # Arrange
        expected_match = riot_fixtures.match_fixture
        crud.put_match(expected_match)

        # Act
        match_from_db = crud.get_match_by_id(expected_match.id)

        # Assert
        self.assertIsNotNone(match_from_db)
        self.assertIsInstance(match_from_db, Match)
        self.assertEqual(expected_match, match_from_db)

    def test_get_match_by_id_no_existing_match(self):
        # Arrange
        expected_match = riot_fixtures.match_fixture

        # Act
        match_from_db = crud.get_match_by_id(expected_match.id)

        # Assert
        self.assertIsNone(match_from_db)

    def test_get_match_ids_without_games_matches_with_no_games(self):
        # Arrange
        match_with_has_games = riot_fixtures.match_fixture.model_copy(deep=True)
        match_with_has_games.has_games = True
        crud.put_match(match_with_has_games)

        match_without_has_games = match_with_has_games.model_copy(deep=True)
        match_without_has_games.id = RiotMatchID("123")
        match_without_has_games.has_games = False
        crud.put_match(match_without_has_games)

        game_for_future_match = riot_fixtures.game_1_fixture_unstarted_future_match
        crud.put_game(game_for_future_match)

        # Act
        match_ids_without_games = crud.get_match_ids_without_games()

        # Assert
        self.assertNotEqual(game_for_future_match.match_id, match_with_has_games.id)
        self.assertNotEqual(game_for_future_match.match_id, match_without_has_games.id)
        self.assertIsInstance(match_ids_without_games, list)
        self.assertEqual(1, len(match_ids_without_games))
        self.assertEqual(match_with_has_games.id, match_ids_without_games[0])

    def test_get_match_ids_without_games_matches_with_games(self):
        # Arrange
        match_with_has_games = riot_fixtures.match_fixture.model_copy(deep=True)
        match_with_has_games.has_games = True
        crud.put_match(match_with_has_games)

        match_without_has_games = match_with_has_games.model_copy(deep=True)
        match_without_has_games.id = RiotMatchID("123")
        match_without_has_games.has_games = False
        crud.put_match(match_without_has_games)

        match_1_game = riot_fixtures.game_1_fixture_completed.model_copy(deep=True)
        match_1_game.match_id = match_with_has_games.id
        crud.put_game(match_1_game)

        match_2_game = riot_fixtures.game_2_fixture_inprogress.model_copy(deep=True)
        match_2_game.match_id = match_without_has_games.id
        crud.put_game(match_2_game)

        # Act
        match_ids_without_games = crud.get_match_ids_without_games()

        # Assert
        self.assertEqual(match_1_game.match_id, match_with_has_games.id)
        self.assertEqual(match_2_game.match_id, match_without_has_games.id)
        self.assertIsInstance(match_ids_without_games, list)
        self.assertEqual(0, len(match_ids_without_games))

    def test_update_match_has_games(self):
        # Arrange
        match = riot_fixtures.match_fixture.model_copy(deep=True)
        match.has_games = True
        crud.put_match(match)

        new_has_games = not match.has_games
        updated_match = match.model_copy(deep=True)
        updated_match.has_games = new_has_games

        # Act and Assert
        self.assertEqual(match.id, updated_match.id)
        self.assertNotEqual(match.has_games, new_has_games)
        match_before_update = crud.get_match_by_id(match.id)
        self.assertEqual(match, match_before_update)
        crud.update_match_has_games(match.id, new_has_games)
        match_after_update = crud.get_match_by_id(match.id)
        self.assertEqual(updated_match, match_after_update)

        with self.assertRaises(AssertionError):
            crud.update_match_has_games(RiotMatchID("123"), new_has_games)
