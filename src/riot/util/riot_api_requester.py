from http import HTTPStatus
import cloudscraper  # type: ignore
import logging
import certifi

import pydantic
import requests
from requests import Response

from src.common.schemas.riot_data_schemas import (
    League,
    RiotLeagueID,
    ProfessionalPlayer,
    ProfessionalTeam,
    Tournament,
    RiotTournamentID,
    Match,
    RiotMatchID,
    GetGamesResponseSchema,
    Game,
    RiotGameID,
    PlayerGameMetadata,
    PlayerGameStats,
    Schedule,
    SchedulePages
)
from src.common import app_config

from src.riot.exceptions import RiotApiStatusCodeAssertException

logger = logging.getLogger('riot')


class RiotApiRequester:
    def __init__(self):
        self.esports_api_url = app_config.ESPORTS_API_URL
        self.esports_feed_url = app_config.ESPORTS_FEED_URL
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
            "x-api-key": app_config.RIOT_API_KEY
        }

    def make_request(self, url, headers=None) -> Response:
        if headers is None:
            headers = self.default_headers

        try:
            response = self.client.get(url, headers=headers, verify=certifi.where())
            response.raise_for_status()
            logger.info(
                f"API Request: GET {url} | Headers: {headers} "
                f"| Response: {response.status_code} {response.text[:500]}"
            )
            return response
        except requests.RequestException as e:
            logger.error(f"API Request Failed: GET {url} | Headers: {headers} | Error: {e}")
            raise

    def get_games_from_event_details(self, match_id: RiotMatchID) -> list[Game]:
        event_details_url = f"{self.esports_api_url}/getEventDetails?hl=en-GB&id={match_id}"
        response = self.make_request(event_details_url)
        validate_response(
            [HTTPStatus.OK, HTTPStatus.NO_CONTENT],
            response.status_code,
            event_details_url
        )
        if response.status_code == HTTPStatus.NO_CONTENT:
            return []

        try:
            res_json = response.json()
            data = res_json['data']
            event = data['event']
            match = event['match']
            games = match['games']
        except TypeError:
            return []

        games_from_response = []
        for game in games:
            new_game = Game(
                id=game['id'],
                state=game['state'],
                number=game['number'],
                match_id=event['id']
            )
            games_from_response.append(new_game)
        return games_from_response

    def get_games(self, game_ids: list[RiotGameID]) -> list[GetGamesResponseSchema]:
        game_ids_str = ','.join(map(str, game_ids))
        url = f"{self.esports_api_url}/getGames?hl=en-GB&id={game_ids_str}"
        response = self.make_request(url)
        validate_response([HTTPStatus.OK], response.status_code, url)

        res_json = response.json()
        games = res_json['data']['games']
        games_from_response = []
        for game in games:
            game_response = GetGamesResponseSchema(
                id=game['id'],
                state=game['state']
            )
            games_from_response.append(game_response)
        return games_from_response

    def get_leagues(self) -> list[League]:
        url = f"{self.esports_api_url}/getLeagues?hl=en-GB"
        response = self.make_request(url)
        validate_response([HTTPStatus.OK], response.status_code, url)

        res_json = response.json()
        leagues_from_response = []
        for league in res_json['data']['leagues']:
            new_league = League(
                id=league['id'],
                slug=league['slug'],
                name=league['name'],
                region=league['region'],
                image=league['image'],
                priority=league['priority']
            )
            leagues_from_response.append(new_league)
        return leagues_from_response

    def get_tournament_for_league(self, league_id: RiotLeagueID) -> list[Tournament]:
        url = f"{self.esports_api_url}/getTournamentsForLeague?hl=en-GB&leagueId={league_id}"
        tournaments_from_response: list[Tournament] = []

        response = self.make_request(url)
        validate_response([HTTPStatus.OK], response.status_code, url)

        res_json = response.json()
        leagues = res_json['data']['leagues']
        if len(leagues) == 0:
            logger.debug(f"No tournaments found for league with ID {league_id}")
            return tournaments_from_response

        tournaments = leagues[0]['tournaments']
        for tournament in tournaments:
            new_tournament = Tournament(
                id=tournament['id'],
                slug=tournament['slug'],
                start_date=tournament['startDate'],
                end_date=tournament['endDate'],
                league_id=league_id
            )
            tournaments_from_response.append(new_tournament)
        return tournaments_from_response

    def get_teams(self) -> list[ProfessionalTeam]:
        url = f"{self.esports_api_url}/getTeams?hl=en-GB"
        response = self.make_request(url)
        validate_response([HTTPStatus.OK], response.status_code, url)

        res_json = response.json()
        teams_from_response = []
        for team in res_json['data']['teams']:
            # Validate the team data
            for key in team.keys():
                if team[key] is None:
                    team[key] = 'None'
            if team['homeLeague'] != 'None':
                team['homeLeague'] = team['homeLeague']['name']

            new_team = ProfessionalTeam(
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

    def get_players(self) -> list[ProfessionalPlayer]:
        url = f"{self.esports_api_url}/getTeams?hl=en-GB"
        response = self.make_request(url)
        validate_response([HTTPStatus.OK], response.status_code, url)

        res_json = response.json()
        players_from_response = []
        for team in res_json['data']['teams']:
            for player in team['players']:
                new_player = ProfessionalPlayer(
                    id=player['id'],
                    summoner_name=player['summonerName'],
                    image=player['image'],
                    role=player['role'],
                    team_id=team['id']
                )
                players_from_response.append(new_player)
        return players_from_response

    def get_player_metadata_for_game(self, game_id: RiotGameID, time_stamp: str) \
            -> list[PlayerGameMetadata]:
        url = f"{self.esports_feed_url}/window/{game_id}?hl=en-GB&startingTime={time_stamp}"
        response = self.make_request(url)
        validate_response(
            [HTTPStatus.OK, HTTPStatus.NO_CONTENT],
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

    def get_player_stats_for_game(self, game_id: RiotGameID, time_stamp: str) \
            -> list[PlayerGameStats]:
        url = f"{self.esports_feed_url}/details/{game_id}?hl=en-GB&startingTime={time_stamp}"
        response = self.make_request(url)
        validate_response(
            [HTTPStatus.OK, HTTPStatus.NO_CONTENT],
            response.status_code,
            url
        )
        if response.status_code == HTTPStatus.NO_CONTENT:
            return []

        res_json = response.json()
        player_stats_from_response: list[PlayerGameStats] = []
        frames = res_json.get("frames", [])
        if len(frames) < 1:
            logger.error(
                f"No frames fetched for game id {game_id} with time stamp {time_stamp}"
            )
            return player_stats_from_response

        last_frame = frames[len(frames) - 1]
        participants = last_frame.get("participants", [])
        for participant in participants:
            new_player_stats = PlayerGameStats(
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

    def get_schedule(self, page_token: str | None = None) -> Schedule:
        schedule_response = self.__get_schedule(page_token)
        pages = SchedulePages(
            older_token=schedule_response['pages']['older'],
            newer_token=schedule_response['pages']['newer']
        )
        matches = self.__get_matches_from_schedule(schedule_response)
        schedule = Schedule(
            schedule_pages=pages,
            matches=matches
        )
        return schedule

    def get_tournament_id_for_match(self, match_id: RiotMatchID) -> RiotTournamentID:
        url = f"{self.esports_api_url}/getEventDetails?hl=en-GB&id={match_id}"
        response = self.make_request(url)
        validate_response([HTTPStatus.OK], response.status_code, url)

        res_json = response.json()
        return RiotTournamentID(res_json['data']['event']['tournament']['id'])

    def __get_schedule(self, page_token: str | None = None) -> dict:
        if page_token is None:
            url = f"{self.esports_api_url}/getSchedule?hl=en-GB"
        else:
            url = f"{self.esports_api_url}/getSchedule?hl=en-GB&pageToken={page_token}"

        response = self.make_request(url)
        if response.status_code != HTTPStatus.OK:
            raise RiotApiStatusCodeAssertException([HTTPStatus.OK], response.status_code, url)

        res_json = response.json()
        return res_json["data"].get("schedule", {})

    def __get_matches_from_schedule(self, schedule: dict) -> list[Match]:
        matches_from_response = []
        events = schedule.get("events", [])
        for event in events:
            if event['type'] != 'match':
                continue

            match = event['match']

            team_1_wins = None
            team_2_wins = None
            winning_team = None
            if event['state'] in ["completed", "inProgress"]:
                if match['teams'][0]['result'] is not None:
                    team_1_wins = match['teams'][0]['result']['gameWins']
                if match['teams'][1]['result'] is not None:
                    team_2_wins = match['teams'][1]['result']['gameWins']

            if event['state'] == "completed":
                if match['teams'][0]['result']['outcome'] == "win":
                    winning_team = match['teams'][0]['name']
                else:
                    winning_team = match['teams'][1]['name']

            new_match = Match(
                id=match['id'],
                start_time=event['startTime'],
                block_name=event['blockName'],
                league_slug=event['league']['slug'],
                strategy_type=match['strategy']['type'],
                strategy_count=match['strategy']['count'],
                tournament_id=self.get_tournament_id_for_match(match['id']),
                team_1_name=match['teams'][0]['name'],
                team_2_name=match['teams'][1]['name'],
                state=event['state'],
                team_1_wins=team_1_wins,
                team_2_wins=team_2_wins,
                winning_team=winning_team
            )
            matches_from_response.append(new_match)
        return matches_from_response


def validate_response(expected_status: list[HTTPStatus], status_code: int, url) -> None:
    if status_code not in expected_status:
        raise RiotApiStatusCodeAssertException(expected_status, status_code, url)


def parse_team_metadata(team_metadata: dict, game_id: RiotGameID) \
        -> list[PlayerGameMetadata]:
    participant_metadata = team_metadata.get("participantMetadata", [])
    player_metadata_for_team = []
    for participant in participant_metadata:
        new_player_metadata = PlayerGameMetadata(
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
