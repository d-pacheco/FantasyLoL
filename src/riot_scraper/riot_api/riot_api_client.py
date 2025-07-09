from http import HTTPStatus
import logging
from requests import Response

from src.common.schemas.riot_data_schemas import RiotLeagueID, RiotMatchID, RiotGameID
from src.common import app_config
from src.riot_scraper.riot_api.api_requester import ApiRequester
from src.riot_scraper.riot_api.api_status_code_assert_exception import ApiStatusCodeAssertException
from src.riot_scraper.riot_api.schemas.get_event_details import EventDetailsResponse
from src.riot_scraper.riot_api.schemas.get_games import GetGamesResponse
from src.riot_scraper.riot_api.schemas.get_leagues import GetLeaguesResponse
from src.riot_scraper.riot_api.schemas.get_live_details import GetLiveDetailsResponse
from src.riot_scraper.riot_api.schemas.get_live_window import GetLiveWindowResponse
from src.riot_scraper.riot_api.schemas.get_schedule import GetScheduleResponse
from src.riot_scraper.riot_api.schemas.get_teams import GetTeamsResponse
from src.riot_scraper.riot_api.schemas.get_tournament import GetTournamentsResponse

logger = logging.getLogger('scraper')


class RiotApiClient:
    def __init__(self, api_requester: ApiRequester):
        self.api_requester = api_requester
        self.esports_api_url = app_config.ESPORTS_API_URL
        self.esports_feed_url = app_config.ESPORTS_FEED_URL
        self.default_headers = {
            "Origin": "https://lolesports.com",
            "Referrer": "https://lolesports.com",
            "x-api-key": app_config.RIOT_API_KEY
        }

    def make_request(self, url, headers=None) -> Response:
        if headers is None:
            headers = self.default_headers
        return self.api_requester.make_request(url, headers)

    def get_event_details(self, match_id: RiotMatchID) -> EventDetailsResponse | None:
        event_details_url = f"{self.esports_api_url}/getEventDetails?hl=en-GB&id={match_id}"
        response = self.make_request(event_details_url)
        validate_response(
            [HTTPStatus.OK, HTTPStatus.NO_CONTENT],
            response.status_code,
            event_details_url
        )
        if response.status_code == HTTPStatus.NO_CONTENT:
            return None
        else:
            return EventDetailsResponse.model_validate(response.json())

    def get_games(self, game_ids: list[RiotGameID]) -> GetGamesResponse:
        game_ids_str = ','.join(map(str, game_ids))
        url = f"{self.esports_api_url}/getGames?hl=en-GB&id={game_ids_str}"
        response = self.make_request(url)
        validate_response([HTTPStatus.OK], response.status_code, url)

        return GetGamesResponse.model_validate(response.json())

    def get_leagues(self) -> GetLeaguesResponse:
        url = f"{self.esports_api_url}/getLeagues?hl=en-GB"
        response = self.make_request(url)
        validate_response([HTTPStatus.OK], response.status_code, url)

        return GetLeaguesResponse.model_validate(response.json())

    def get_tournament_for_league(self, league_id: RiotLeagueID) -> GetTournamentsResponse:
        url = f"{self.esports_api_url}/getTournamentsForLeague?hl=en-GB&leagueId={league_id}"
        response = self.make_request(url)
        validate_response([HTTPStatus.OK], response.status_code, url)

        return GetTournamentsResponse.model_validate(response.json())

    def get_teams(self) -> GetTeamsResponse:
        url = f"{self.esports_api_url}/getTeams?hl=en-GB"
        response = self.make_request(url)
        validate_response([HTTPStatus.OK], response.status_code, url)

        return GetTeamsResponse.model_validate(response.json())

    def get_game_window(
            self,
            game_id: RiotGameID,
            time_stamp: str | None = None
    ) -> GetLiveWindowResponse | None:
        if time_stamp:
            url = f"{self.esports_feed_url}/window/{game_id}?hl=en-GB&startingTime={time_stamp}"
        else:
            url = f"{self.esports_feed_url}/window/{game_id}?hl=en-GB"
        response = self.make_request(url)
        validate_response(
            [HTTPStatus.OK, HTTPStatus.NO_CONTENT],
            response.status_code,
            url
        )
        if response.status_code == HTTPStatus.NO_CONTENT:
            return None

        return GetLiveWindowResponse.model_validate(response.json())

    def get_game_details(
            self,
            game_id: RiotGameID,
            time_stamp: str
    ) -> GetLiveDetailsResponse | None:
        url = f"{self.esports_feed_url}/details/{game_id}?hl=en-GB&startingTime={time_stamp}"
        response = self.make_request(url)
        validate_response(
            [HTTPStatus.OK, HTTPStatus.NO_CONTENT],
            response.status_code,
            url
        )
        if response.status_code == HTTPStatus.NO_CONTENT:
            return None

        return GetLiveDetailsResponse.model_validate(response.json())

    def get_schedule(self, page_token: str | None = None) -> GetScheduleResponse:
        if page_token is None:
            url = f"{self.esports_api_url}/getSchedule?hl=en-GB"
        else:
            url = f"{self.esports_api_url}/getSchedule?hl=en-GB&pageToken={page_token}"

        response = self.make_request(url)
        validate_response([HTTPStatus.OK], response.status_code, url)

        return GetScheduleResponse.model_validate(response.json())


def validate_response(expected_status: list[HTTPStatus], status_code: int, url) -> None:
    if status_code not in expected_status:
        raise ApiStatusCodeAssertException(expected_status, status_code, url)
