import random

from src.common.schemas.riot_data_schemas import (
    PlayerRole,
    ProPlayerID,
    RiotGameID,
    PlayerGameMetadata
)
from src.db import crud
from tests.test_base import FantasyLolTestBase
from tests.test_util import riot_fixtures


class TestCrudRiotPlayerMetadata(FantasyLolTestBase):
    def test_put_player_metadata_no_existing_player_metadata(self):
        # Arrange
        player_metadata = riot_fixtures.player_1_game_metadata_fixture

        # Act and Assert
        player_metadata_before_put = crud.get_player_metadata(
            player_metadata.player_id, player_metadata.game_id
        )
        self.assertIsNone(player_metadata_before_put)
        crud.put_player_metadata(player_metadata)
        player_metadata_after_put = crud.get_player_metadata(
            player_metadata.player_id, player_metadata.game_id
        )
        self.assertEqual(player_metadata, player_metadata_after_put)

    def test_put_player_metadata_existing_player_metadata(self):
        # Arrange
        player_metadata = riot_fixtures.player_1_game_metadata_fixture
        crud.put_player_metadata(player_metadata)
        updated_player_metadata = player_metadata.model_copy(deep=True)
        updated_player_metadata.champion_id = "updatedChampionId"

        # Act and Assert
        player_metadata_before_put = crud.get_player_metadata(
            player_metadata.player_id, player_metadata.game_id
        )
        self.assertEqual(player_metadata, player_metadata_before_put)
        self.assertEqual(player_metadata.player_id, updated_player_metadata.player_id)
        self.assertEqual(player_metadata.game_id, updated_player_metadata.game_id)
        crud.put_player_metadata(updated_player_metadata)
        player_metadata_after_put = crud.get_player_metadata(
            player_metadata.player_id, player_metadata.game_id
        )
        self.assertEqual(updated_player_metadata, player_metadata_after_put)

    def test_get_player_metadata(self):
        # Arrange
        player_metadata = riot_fixtures.player_1_game_metadata_fixture
        crud.put_player_metadata(player_metadata)

        # Act and Assert
        self.assertEqual(
            player_metadata,
            crud.get_player_metadata(player_metadata.player_id, player_metadata.game_id)
        )
        self.assertIsNone(crud.get_player_metadata(ProPlayerID("123"), player_metadata.game_id))
        self.assertIsNone(crud.get_player_metadata(player_metadata.player_id, RiotGameID("123")))

    def test_get_games_without_player_metadata_completed_game_without_10_rows(self):
        game = riot_fixtures.game_1_fixture_completed
        crud.put_game(game)
        game_ids = crud.get_game_ids_without_player_metadata()
        self.assertIsInstance(game_ids, list)
        self.assertEqual(1, len(game_ids))
        self.assertEqual(game.id, game_ids[0])

    def test_get_games_without_player_metadata_completed_game_with_10_rows(self):
        game = riot_fixtures.game_1_fixture_completed
        crud.put_game(game)
        for participant_id in range(1, 11):
            create_player_metadata(game.id, participant_id)
        game_ids = crud.get_game_ids_without_player_metadata()
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_get_games_without_player_metadata_inprogress_game_without_10_rows(self):
        game = riot_fixtures.game_2_fixture_inprogress
        crud.put_game(game)
        game_ids = crud.get_game_ids_without_player_metadata()
        self.assertIsInstance(game_ids, list)
        self.assertEqual(1, len(game_ids))
        self.assertEqual(game.id, game_ids[0])

    def test_get_games_without_player_metadata_inprogress_game_with_10_rows(self):
        game = riot_fixtures.game_2_fixture_inprogress
        crud.put_game(game)
        for participant_id in range(1, 11):
            create_player_metadata(game.id, participant_id)
        game_ids = crud.get_game_ids_without_player_metadata()
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))

    def test_get_games_without_player_metadata_unstarted_game_without_10_rows(self):
        game = riot_fixtures.game_3_fixture_unstarted
        crud.put_game(game)
        game_ids = crud.get_game_ids_without_player_metadata()
        self.assertIsInstance(game_ids, list)
        self.assertEqual(0, len(game_ids))


def create_player_metadata(game_id: RiotGameID, participant_id: int):
    if participant_id % 5 == 1:
        role = PlayerRole.TOP
    elif participant_id % 5 == 2:
        role = PlayerRole.JUNGLE
    elif participant_id % 5 == 3:
        role = PlayerRole.MID
    elif participant_id % 5 == 4:
        role = PlayerRole.BOTTOM
    else:
        role = PlayerRole.SUPPORT

    player_metadata = PlayerGameMetadata(
        game_id=game_id,
        player_id=ProPlayerID(str(random.randint(1, 9999999))),
        participant_id=participant_id,
        champion_id=f"championId{participant_id}",
        role=role
    )
    crud.put_player_metadata(player_metadata)
