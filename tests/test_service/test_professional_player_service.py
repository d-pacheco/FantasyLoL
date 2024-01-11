import random
from tests.fantasy_lol_test_base import FantasyLolTestBase
from tests.riot_api_requester_util import RiotApiRequestUtil

from fantasylol.db.database import DatabaseConnection
from fantasylol.exceptions.professional_player_not_found_exception import \
    ProfessionalPlayerNotFoundException
from fantasylol.service.riot_professional_player_service import RiotProfessionalPlayerService
from fantasylol.schemas.search_parameters import PlayerSearchParameters


def create_professional_player_service():
    return RiotProfessionalPlayerService()


class ProfessionalPlayerServiceTest(FantasyLolTestBase):
    def setUp(self):
        self.riot_api_util = RiotApiRequestUtil()

    def create_professional_player_and_team_in_db(self):
        mock_player = self.riot_api_util.create_mock_player()
        mock_team = self.riot_api_util.create_mock_team()
        with DatabaseConnection() as db:
            db.add(mock_team)
            db.commit()
            db.add(mock_player)
            db.commit()
            db.refresh(mock_team)
            db.refresh(mock_player)
        return mock_player, mock_team

    def test_get_existing_professional_players_by_summoner_name(self):
        expected_player, expected_team = self.create_professional_player_and_team_in_db()
        search_parameters = PlayerSearchParameters(summoner_name=expected_player.summoner_name)

        professional_player_service = create_professional_player_service()
        players_from_db = professional_player_service.get_players(search_parameters)
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(1, len(players_from_db))
        self.assertEqual(expected_player, players_from_db[0])

    def test_get_no_existing_professional_players_by_summoner_name(self):
        self.create_professional_player_and_team_in_db()
        search_parameters = PlayerSearchParameters(summoner_name="badSummonerName")

        professional_player_service = create_professional_player_service()
        players_from_db = professional_player_service.get_players(search_parameters)
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(0, len(players_from_db))

    def test_get_existing_professional_players_by_role(self):
        expected_player, expected_team = self.create_professional_player_and_team_in_db()
        search_parameters = PlayerSearchParameters(role=expected_player.role)

        professional_player_service = create_professional_player_service()
        players_from_db = professional_player_service.get_players(search_parameters)
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(1, len(players_from_db))
        self.assertEqual(expected_player, players_from_db[0])

    def test_get_no_existing_professional_players_by_role(self):
        self.create_professional_player_and_team_in_db()
        search_parameters = PlayerSearchParameters(role="badRole")

        professional_player_service = create_professional_player_service()
        players_from_db = professional_player_service.get_players(search_parameters)
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(0, len(players_from_db))

    def test_get_existing_professional_players_by_team_id(self):
        expected_player, expected_team = self.create_professional_player_and_team_in_db()
        search_parameters = PlayerSearchParameters(team_id=expected_player.team_id)

        professional_player_service = create_professional_player_service()
        players_from_db = professional_player_service.get_players(search_parameters)
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(1, len(players_from_db))
        self.assertEqual(expected_player, players_from_db[0])

    def test_get_no_existing_professional_players_by_team_id(self):
        self.create_professional_player_and_team_in_db()
        search_parameters = PlayerSearchParameters(team_id=random.randint(1, 100000))

        professional_player_service = create_professional_player_service()
        players_from_db = professional_player_service.get_players(search_parameters)
        self.assertIsInstance(players_from_db, list)
        self.assertEqual(0, len(players_from_db))

    def test_get_professional_player_by_id(self):
        expected_player, expected_team = self.create_professional_player_and_team_in_db()
        professional_player_service = create_professional_player_service()
        player_from_db = professional_player_service.get_player_by_id(expected_player.id)
        self.assertEqual(player_from_db, expected_player)

    def test_get_professional_player_by_id_invalid_id(self):
        self.create_professional_player_and_team_in_db()
        professional_player_service = create_professional_player_service()
        with self.assertRaises(ProfessionalPlayerNotFoundException):
            professional_player_service.get_player_by_id(random.randint(1, 100000))
