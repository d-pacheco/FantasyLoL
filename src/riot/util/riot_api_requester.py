import cloudscraper
from http import HTTPStatus
import logging

import pydantic
from requests import Response
from typing import List

from ...common.schemas import riot_data_schemas as schemas
from ...common.config import Config

from ..exceptions.riot_api_status_code_assert_exception import RiotApiStatusCodeAssertException

logger = logging.getLogger('fantasy-lol')


class RiotApiRequester:
    def __init__(self):
        self.esports_api_url = Config.ESPORTS_API_URL
        self.esports_feed_url = Config.ESPORTS_FEED_URL
        self.client = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            },
            debug=False
        )
        self.default_headers = {
            "Origin": "https://lolesports.com",
            "Referrer": "https://lolesports.com",
            "x-api-key": Config.RIOT_API_KEY
        }

    def make_request(self, url, headers=None) -> Response:
        if headers is None:
            headers = self.default_headers
        return self.client.get(url, headers=headers)

    def get_games_from_event_details(self, match_id: str) -> List[schemas.Game]:
        event_details_url = f"{self.esports_api_url}/getEventDetails?hl=en-GB&id={match_id}"
        response = self.make_request(event_details_url)
        if response.status_code != HTTPStatus.OK and response.status_code != HTTPStatus.NO_CONTENT:
            raise RiotApiStatusCodeAssertException(
                f"{HTTPStatus.OK} or {HTTPStatus.NO_CONTENT}",
                response.status_code,
                event_details_url
            )
        if response.status_code == HTTPStatus.NO_CONTENT:
            return []

        res_json = response.json()
        event = res_json['data']['event']
        games = event['match']['games']

        games_from_response = []
        for game in games:
            new_game = schemas.Game(
                id=game['id'],
                state=game['state'],
                number=game['number'],
                match_id=event['id']
            )
            games_from_response.append(new_game)
        return games_from_response

    def get_games(self, game_ids: List[str]) -> List[schemas.GetGamesResponseSchema]:
        game_ids_str = ','.join(map(str, game_ids))
        url = f"{self.esports_api_url}/getGames?hl=en-GB&id={game_ids_str}"
        response = self.make_request(url)
        if response.status_code != HTTPStatus.OK:
            raise RiotApiStatusCodeAssertException(HTTPStatus.OK, response.status_code, url)

        res_json = response.json()
        games = res_json['data']['games']
        games_from_response = []
        for game in games:
            game_response = schemas.GetGamesResponseSchema(
                id=game['id'],
                state=game['state']
            )
            games_from_response.append(game_response)
        return games_from_response

    def get_leagues(self) -> List[schemas.League]:
        url = f"{self.esports_api_url}/getLeagues?hl=en-GB"
        response = self.make_request(url)
        if response.status_code != HTTPStatus.OK:
            raise RiotApiStatusCodeAssertException(HTTPStatus.OK, response.status_code, url)

        res_json = response.json()
        leagues_from_response = []
        for league in res_json['data']['leagues']:
            new_league = schemas.League(
                id=league['id'],
                slug=league['slug'],
                name=league['name'],
                region=league['region'],
                image=league['image'],
                priority=league['priority']
            )
            leagues_from_response.append(new_league)
        return leagues_from_response

    def get_tournament_for_league(self, league_id: int) -> List[schemas.Tournament]:
        url = f"{self.esports_api_url}/getTournamentsForLeague?hl=en-GB&leagueId={league_id}"
        response = self.make_request(url)
        if response.status_code != HTTPStatus.OK:
            raise RiotApiStatusCodeAssertException(HTTPStatus.OK, response.status_code, url)

        res_json = response.json()
        tournaments_from_response = []
        tournaments = res_json['data']['leagues'][0]['tournaments']
        for tournament in tournaments:
            new_tournament = schemas.Tournament(
                id=tournament['id'],
                slug=tournament['slug'],
                start_date=tournament['startDate'],
                end_date=tournament['endDate'],
                league_id=league_id
            )
            tournaments_from_response.append(new_tournament)
        return tournaments_from_response

    def get_teams(self) -> List[schemas.ProfessionalTeam]:
        url = f"{self.esports_api_url}/getTeams?hl=en-GB"
        response = self.make_request(url)
        if response.status_code != HTTPStatus.OK:
            raise RiotApiStatusCodeAssertException(HTTPStatus.OK, response.status_code, url)

        res_json = response.json()
        teams_from_response = []
        for team in res_json['data']['teams']:
            # Validate the team data
            for key in team.keys():
                if team[key] is None:
                    team[key] = 'None'
            if team['homeLeague'] != 'None':
                team['homeLeague'] = team['homeLeague']['name']

            new_team = schemas.ProfessionalTeam(
                id=team['id'],
                slug=team['slug'],
                name=team['name'],
                code=team['code'],
                image=team['image'],
                alternative_image=team['alternativeImage'],
                background_image=team['backgroundImage'],
                status=team['status'],
                home_league=team['homeLeague']
            )
            teams_from_response.append(new_team)
        return teams_from_response

    def get_players(self) -> List[schemas.ProfessionalPlayer]:
        url = f"{self.esports_api_url}/getTeams?hl=en-GB"
        response = self.make_request(url)
        if response.status_code != HTTPStatus.OK:
            raise RiotApiStatusCodeAssertException(HTTPStatus.OK, response.status_code, url)

        res_json = response.json()
        players_from_response = []
        for team in res_json['data']['teams']:
            for player in team['players']:
                new_player = schemas.ProfessionalPlayer(
                    id=player['id'],
                    summoner_name=player['summonerName'],
                    image=player['image'],
                    role=player['role'],
                    team_id=team['id']
                )
                players_from_response.append(new_player)
        return players_from_response

    def get_player_metadata_for_game(self, game_id: str, time_stamp: str) \
            -> List[schemas.PlayerGameMetadata]:
        url = f"{self.esports_feed_url}/window/{game_id}?hl=en-GB&startingTime={time_stamp}"
        response = self.make_request(url)
        if response.status_code != HTTPStatus.OK and response.status_code != HTTPStatus.NO_CONTENT:
            raise RiotApiStatusCodeAssertException(
                f"{HTTPStatus.OK} or {HTTPStatus.NO_CONTENT}",
                response.status_code,
                url
            )
        if response.status_code == HTTPStatus.NO_CONTENT:
            return []

        res_json = response.json()
        game_metadata = res_json.get("gameMetadata", {})
        blue_team_metadata = game_metadata.get("blueTeamMetadata", {})
        red_team_metadata = game_metadata.get("redTeamMetadata", {})
        try:
            blue_team_player_metadata = parse_team_metadata(blue_team_metadata, game_id)
            red_team_player_metadata = parse_team_metadata(red_team_metadata, game_id)
        except pydantic.ValidationError:
            logger.error(f"Error validating player metadata for game id {game_id}")
            return []
        player_metadata_from_response = blue_team_player_metadata + red_team_player_metadata
        return player_metadata_from_response

    def get_player_stats_for_game(self, game_id: str, time_stamp: str) \
            -> List[schemas.PlayerGameStats]:
        url = f"{self.esports_feed_url}/details/{game_id}?hl=en-GB&startingTime={time_stamp}"
        response = self.make_request(url)
        if response.status_code != HTTPStatus.OK and response.status_code != HTTPStatus.NO_CONTENT:
            raise RiotApiStatusCodeAssertException(
                f"{HTTPStatus.OK} or {HTTPStatus.NO_CONTENT}",
                response.status_code,
                url
            )
        if response.status_code == HTTPStatus.NO_CONTENT:
            return []

        res_json = response.json()
        player_stats_from_response = []
        frames = res_json.get("frames", [])
        if len(frames) < 1:
            logger.error(
                f"No frames fetched for game id {game_id} with time stamp {time_stamp}"
            )
            return player_stats_from_response

        last_frame = frames[len(frames) - 1]
        participants = last_frame.get("participants", [])
        for participant in participants:
            new_player_stats = schemas.PlayerGameStats(
                game_id=game_id,
                participant_id=participant['participantId'],
                kills=participant['kills'],
                deaths=participant['deaths'],
                assists=participant['assists'],
                total_gold=participant['totalGoldEarned'],
                creep_score=participant['creepScore'],
                kill_participation=to_rounded_percentage(participant['killParticipation']),
                champion_damage_share=to_rounded_percentage(participant['championDamageShare']),
                wards_placed=participant['wardsPlaced'],
                wards_destroyed=participant['wardsDestroyed']
            )
            player_stats_from_response.append(new_player_stats)
        return player_stats_from_response

    def get_pages_from_schedule(self, page_token: str = None) -> schemas.RiotSchedulePages:
        schedule = self.__get_schedule(page_token)
        pages = schemas.RiotSchedulePages(
            older=schedule['pages']['older'],
            newer=schedule['pages']['newer']
        )
        return pages

    def get_matches_from_schedule(self, page_token: str = None) -> List[schemas.Match]:
        schedule = self.__get_schedule(page_token)
        matches_from_response = []
        events = schedule.get("events", [])
        for event in events:
            if event['type'] != 'match':
                continue
            match = event['match']
            new_match = schemas.Match(
                id=match['id'],
                start_time=event['startTime'],
                block_name=event['blockName'],
                league_slug=event['league']['slug'],
                strategy_type=match['strategy']['type'],
                strategy_count=match['strategy']['count'],
                tournament_id=self.get_tournament_id_for_match(match['id']),
                team_1_name=match['teams'][0]['name'],
                team_2_name=match['teams'][1]['name']
            )
            matches_from_response.append(new_match)
        return matches_from_response

    def get_tournament_id_for_match(self, match_id: str) -> str:
        url = f"{self.esports_api_url}/getEventDetails?hl=en-GB&id={match_id}"
        response = self.make_request(url)
        if response.status_code != HTTPStatus.OK:
            raise RiotApiStatusCodeAssertException(HTTPStatus.OK, response.status_code, url)

        res_json = response.json()
        return res_json['data']['event']['tournament']['id']

    def __get_schedule(self, page_token: str = None) -> dict:
        if page_token is None:
            url = f"{self.esports_api_url}/getSchedule?hl=en-GB"
        else:
            url = f"{self.esports_api_url}/getSchedule?hl=en-GB&pageToken={page_token}"
        response = self.make_request(url)
        if response.status_code != HTTPStatus.OK:
            raise RiotApiStatusCodeAssertException(HTTPStatus.OK, response.status_code, url)

        res_json = response.json()
        return res_json["data"].get("schedule", {})


def parse_team_metadata(team_metadata: dict, game_id: str) \
        -> List[schemas.PlayerGameMetadata]:
    participant_metadata = team_metadata.get("participantMetadata", [])
    player_metadata_for_team = []
    for participant in participant_metadata:
        new_player_metadata = schemas.PlayerGameMetadata(
            game_id=game_id,
            participant_id=participant['participantId'],
            champion_id=participant['championId'],
            role=participant['role'],
            # Weird edge case where it doesn't exist for some games:
            player_id=participant.get(
                'esportsPlayerId', str(participant['participantId'])
            )
        )
        player_metadata_for_team.append(new_player_metadata)
    return player_metadata_for_team


def to_rounded_percentage(float_value: float):
    return round(float_value * 100)
