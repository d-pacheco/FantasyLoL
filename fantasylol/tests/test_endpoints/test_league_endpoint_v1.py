from fastapi.testclient import TestClient
from http import HTTPStatus

from tests.FantasyLolTestBase import FantasyLolTestBase
from tests.RiotApiRequesterUtil import RiotApiRequestUtil
from db.database import DatabaseConnection
from db.models import League
from main import app

class LeagueEndpointV1Test(FantasyLolTestBase):
    def setUp(self):
        self.client = TestClient(app)
        self.riot_api_util = RiotApiRequestUtil()
        self.mock_league = self.riot_api_util.create_mock_league()
        with DatabaseConnection() as db:
            db.add(self.mock_league)
            db.commit()

    def test_get_riot_leagues(self):
        response = self.client.get("/riot/v1/league")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        leagues = response.json()
        self.assertIsInstance(leagues, list)
        self.assertEqual(len(leagues), 1)

        league_from_request = League(**leagues[0])
        self.assertEqual(league_from_request.id, int(self.riot_api_util.mock_league_id))

    def test_get_riot_leagues_not_found(self):
        response = self.client.get("/riot/v1/league/123123")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        response_msg = response.json()
        self.assertEqual(response_msg['detail'], "League not found")

    def test_get_riot_leagues_name_filter_existing_league(self):
        league_name = self.riot_api_util.mock_league_name
        response = self.client.get(f"/riot/v1/league?name={league_name}")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        leagues = response.json()
        self.assertIsInstance(leagues, list)
        self.assertEqual(len(leagues), 1)

        league_from_request = League(**leagues[0])
        self.assertEqual(league_from_request.id, int(self.riot_api_util.mock_league_id))
    
    def test_get_riot_league_name_filter_no_existing_league(self):
        league_name = "BadLeagueName"
        response = self.client.get(f"/riot/v1/league?name={league_name}")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        leagues = response.json()
        self.assertIsInstance(leagues, list)
        self.assertEqual(len(leagues), 0)

    def test_get_riot_leagues_region_filter_existing_league(self):
        league_region = self.riot_api_util.mock_league_region
        response = self.client.get(f"/riot/v1/league?region={league_region}")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        leagues = response.json()
        self.assertIsInstance(leagues, list)
        self.assertEqual(len(leagues), 1)

        league_from_request = League(**leagues[0])
        self.assertEqual(league_from_request.id, int(self.riot_api_util.mock_league_id))

    def test_get_riot_leagues_region_filter_no_existing_league(self):
        league_region = "BadLeagueName"
        response = self.client.get(f"/riot/v1/league?region={league_region}")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        leagues = response.json()
        self.assertIsInstance(leagues, list)
        self.assertEqual(len(leagues), 0)

    def test_get_riot_leagues_name_and_region_filter_existing_league(self):
        league_name = self.riot_api_util.mock_league_name
        league_region = self.riot_api_util.mock_league_region
        response = self.client.get(f"/riot/v1/league?name={league_name}&region={league_region}")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        leagues = response.json()
        self.assertIsInstance(leagues, list)
        self.assertEqual(len(leagues), 1)

        league_from_request = League(**leagues[0])
        self.assertEqual(league_from_request.id, int(self.riot_api_util.mock_league_id))

    def test_get_riot_league_name_with_mismatch_region_filter(self):
        league_name = self.riot_api_util.mock_league_name
        league_region = "BadLeagueRegion"
        response = self.client.get(f"/riot/v1/league?name={league_name}&region={league_region}")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        leagues = response.json()
        self.assertIsInstance(leagues, list)
        self.assertEqual(len(leagues), 0)

    def test_get_riot_league_region_with_mismatch_name_filter(self):
        league_name = "BadLeagueName"
        league_region = self.riot_api_util.mock_league_region
        response = self.client.get(f"/riot/v1/league?name={league_name}&region={league_region}")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        leagues = response.json()
        self.assertIsInstance(leagues, list)
        self.assertEqual(len(leagues), 0)
