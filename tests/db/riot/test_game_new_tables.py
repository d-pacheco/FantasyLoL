from tests.test_base import TestBase
from tests.test_util import riot_fixtures

from src.common.schemas.riot_data_schemas import (
    GameMetadata,
    GameParticipantPerks,
    GameDragons,
    RiotGameID,
)


class TestGameMetadata(TestBase):
    def setUp(self):
        self.db.put_league(riot_fixtures.league_1_fixture)
        self.db.put_team(riot_fixtures.team_1_fixture)
        self.db.put_team(riot_fixtures.team_2_fixture)
        self.db.put_tournament(riot_fixtures.tournament_fixture)
        self.db.put_match(riot_fixtures.match_fixture)
        self.db.put_game(riot_fixtures.game_1_fixture_completed)

    def test_put_and_get_game_metadata(self):
        game_id = riot_fixtures.game_1_fixture_completed.id
        metadata = GameMetadata(game_id=game_id, patch_version="14.1.1")

        self.assertIsNone(self.db.get_game_metadata(game_id))
        self.db.put_game_metadata(metadata)
        result = self.db.get_game_metadata(game_id)
        self.assertEqual(metadata, result)

    def test_get_game_metadata_not_found(self):
        self.assertIsNone(self.db.get_game_metadata(RiotGameID("nonexistent")))


class TestGameParticipantPerks(TestBase):
    def setUp(self):
        self.db.put_league(riot_fixtures.league_1_fixture)
        self.db.put_team(riot_fixtures.team_1_fixture)
        self.db.put_team(riot_fixtures.team_2_fixture)
        self.db.put_tournament(riot_fixtures.tournament_fixture)
        self.db.put_match(riot_fixtures.match_fixture)
        self.db.put_game(riot_fixtures.game_1_fixture_completed)

    def test_put_and_get_game_participant_perks(self):
        game_id = riot_fixtures.game_1_fixture_completed.id
        perks = GameParticipantPerks(
            game_id=game_id,
            participant_id=1,
            style_id=8100,
            sub_style_id=8300,
            perks=[8112, 8126, 8138, 8135, 8304, 8345],
        )

        self.assertIsNone(self.db.get_game_participant_perks(game_id, 1))
        self.db.put_game_participant_perks(perks)
        result = self.db.get_game_participant_perks(game_id, 1)
        self.assertEqual(perks, result)

    def test_get_game_participant_perks_not_found(self):
        game_id = riot_fixtures.game_1_fixture_completed.id
        self.assertIsNone(self.db.get_game_participant_perks(game_id, 99))


class TestGameDragons(TestBase):
    def setUp(self):
        self.db.put_league(riot_fixtures.league_1_fixture)
        self.db.put_team(riot_fixtures.team_1_fixture)
        self.db.put_team(riot_fixtures.team_2_fixture)
        self.db.put_tournament(riot_fixtures.tournament_fixture)
        self.db.put_match(riot_fixtures.match_fixture)
        self.db.put_game(riot_fixtures.game_1_fixture_completed)

    def test_put_and_get_game_dragons(self):
        game_id = riot_fixtures.game_1_fixture_completed.id
        team_id = riot_fixtures.team_1_fixture.id
        dragon = GameDragons(
            game_id=game_id, dragon_number=1, team_id=team_id, dragon_type="infernal"
        )

        self.assertEqual([], self.db.get_game_dragons(game_id))
        self.db.put_game_dragon(dragon)
        result = self.db.get_game_dragons(game_id)
        self.assertEqual(1, len(result))
        self.assertEqual(dragon, result[0])

    def test_get_game_dragons_empty(self):
        game_id = riot_fixtures.game_1_fixture_completed.id
        self.assertEqual([], self.db.get_game_dragons(game_id))
