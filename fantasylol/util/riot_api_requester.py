import logging
import cloudscraper
from http import HTTPStatus
from requests import Response
from typing import List

from fantasylol.schemas import riot_data_schemas as schemas

from fantasylol.exceptions.riot_api_status_code_assert_exception import \
    RiotApiStatusCodeAssertException

logger = logging.getLogger('fantasy-lol')


class RiotApiRequester:
    def __init__(self):
        RIOT_API_KEY = "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"
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
            "x-api-key": RIOT_API_KEY
        }

    def make_request(self, url, headers=None) -> Response:
        if headers is None:
            headers = self.default_headers
        return self.client.get(url, headers=headers)

    def get_games_from_event_details(self, match_id: str) -> List[schemas.GameSchema]:
        event_details_url = (
            f"https://esports-api.lolesports.com"
            f"/persisted/gw/getEventDetails?hl=en-GB&id={match_id}"
        )
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
            new_game = schemas.GameSchema()
            new_game.id = game['id']
            new_game.state = game['state']
            new_game.number = game['number']
            new_game.match_id = event['id']
            games_from_response.append(new_game)
        return games_from_response

    def get_games(self, game_ids: List[str]) -> List[schemas.GetGamesResponseSchema]:
        game_ids_str = ','.join(map(str, game_ids))
        url = (
            f"https://esports-api.lolesports.com"
            f"/persisted/gw/getGames?hl=en-GB&id={game_ids_str}"
        )
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

    def get_leagues(self) -> List[schemas.LeagueSchema]:
        url = "https://esports-api.lolesports.com/persisted/gw/getLeagues?hl=en-GB"
        response = self.make_request(url)
        if response.status_code != HTTPStatus.OK:
            raise RiotApiStatusCodeAssertException(HTTPStatus.OK, response.status_code, url)

        res_json = response.json()
        leagues_from_response = []
        for league in res_json['data']['leagues']:
            new_league = schemas.LeagueSchema()
            new_league.id = league['id']
            new_league.slug = league['slug']
            new_league.name = league['name']
            new_league.region = league['region']
            new_league.image = league['image']
            new_league.priority = league['priority']
            leagues_from_response.append(new_league)
        return leagues_from_response

    def get_tournament_for_league(self, league_id: int) -> List[schemas.Tournament]:
        url = (
            "https://esports-api.lolesports.com/persisted/gw"
            f"/getTournamentsForLeague?hl=en-GB&leagueId={league_id}"
        )
        response = self.make_request(url)
        if response.status_code != HTTPStatus.OK:
            raise RiotApiStatusCodeAssertException(HTTPStatus.OK, response.status_code, url)

        res_json = response.json()
        tournaments_from_response = []
        tournaments = res_json['data']['leagues'][0]['tournaments']
        for tournament in tournaments:
            new_tournament = schemas.Tournament()
            new_tournament.id = tournament['id']
            new_tournament.slug = tournament['slug']
            new_tournament.start_date = tournament['startDate']
            new_tournament.end_date = tournament['endDate']
            new_tournament.league_id = league_id
            tournaments_from_response.append(new_tournament)
        return tournaments_from_response

    def get_teams(self) -> List[schemas.ProfessionalTeam]:
        url = "https://esports-api.lolesports.com/persisted/gw/getTeams?hl=en-GB"
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

            new_team = schemas.ProfessionalTeam()
            new_team.id = team['id']
            new_team.slug = team['slug']
            new_team.name = team['name']
            new_team.code = team['code']
            new_team.image = team['image']
            new_team.alternative_image = team['alternativeImage']
            new_team.background_image = team['backgroundImage']
            new_team.status = team['status']
            new_team.home_league = team['homeLeague']
            teams_from_response.append(new_team)
        return teams_from_response

    def get_players(self) -> List[schemas.ProfessionalPlayer]:
        url = "https://esports-api.lolesports.com/persisted/gw/getTeams?hl=en-GB"
        response = self.make_request(url)
        if response.status_code != HTTPStatus.OK:
            raise RiotApiStatusCodeAssertException(HTTPStatus.OK, response.status_code, url)

        res_json = response.json()
        players_from_response = []
        for team in res_json['data']['teams']:
            for player in team['players']:
                new_player = schemas.ProfessionalPlayer()
                new_player.id = player['id']
                new_player.summoner_name = player['summonerName']
                new_player.image = player['image']
                new_player.role = player['role']
                new_player.team_id = team['id']
                players_from_response.append(new_player)
        return players_from_response

    def get_player_metadata_for_game(self, game_id: str, time_stamp: str) \
            -> List[schemas.PlayerGameMetadataSchema]:
        url = (
            "https://feed.lolesports.com"
            f"/livestats/v1/window/{game_id}?hl=en-GB&startingTime={time_stamp}"
        )
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
        blue_team_player_metadata = parse_team_metadata(blue_team_metadata, game_id)
        red_team_player_metadata = parse_team_metadata(red_team_metadata, game_id)
        player_metadata_from_response = blue_team_player_metadata + red_team_player_metadata
        return player_metadata_from_response

    def get_player_stats_for_game(self, game_id: str, time_stamp: str) \
            -> List[schemas.PlayerGameStatsSchema]:
        url = (
            "https://feed.lolesports.com"
            f"/livestats/v1/details/{game_id}?hl=en-GB&startingTime={time_stamp}"
        )
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
            new_player_stats = schemas.PlayerGameStatsSchema()
            new_player_stats.game_id = game_id
            new_player_stats.participant_id = participant['participantId']
            new_player_stats.kills = participant['kills']
            new_player_stats.deaths = participant['deaths']
            new_player_stats.assists = participant['assists']
            new_player_stats.total_gold = participant['totalGoldEarned']
            new_player_stats.creep_score = participant['creepScore']
            new_player_stats.kill_participation = participant['killParticipation']
            new_player_stats.champion_damage_share = participant['championDamageShare']
            new_player_stats.wards_placed = participant['wardsPlaced']
            new_player_stats.wards_destroyed = participant['wardsDestroyed']
            player_stats_from_response.append(new_player_stats)
        return player_stats_from_response

    def get_pages_from_schedule(self, page_token: str = None) -> schemas.RiotSchedulePages:
        schedule = self.__get_schedule(page_token)
        pages = schemas.RiotSchedulePages()
        pages.older = schedule['pages']['older']
        pages.newer = schedule['pages']['newer']
        return pages

    def get_matches_from_schedule(self, page_token: str = None) -> List[schemas.MatchSchema]:
        schedule = self.__get_schedule(page_token)
        matches_from_response = []
        events = schedule.get("events", [])
        for event in events:
            match = event['match']
            new_match = schemas.MatchSchema()
            new_match.id = match['id']
            new_match.start_time = event['startTime']
            new_match.block_name = event['blockName']
            new_match.league_slug = event['league']['slug']
            new_match.strategy_type = match['strategy']['type']
            new_match.strategy_count = match['strategy']['count']
            new_match.tournament_id = self.get_tournament_id_for_match(new_match.id)
            new_match.team_1_name = match['teams'][0]['name']
            new_match.team_2_name = match['teams'][1]['name']
            matches_from_response.append(new_match)
        return matches_from_response

    def get_tournament_id_for_match(self, match_id: str) -> str:
        url = (
            "https://esports-api.lolesports.com"
            f"/persisted/gw/getEventDetails?hl=en-GB&id={match_id}"
        )
        response = self.make_request(url)
        if response.status_code != HTTPStatus.OK:
            raise RiotApiStatusCodeAssertException(HTTPStatus.OK, response.status_code, url)

        res_json = response.json()
        return res_json['data']['event']['tournament']['id']

    def __get_schedule(self, page_token: str = None) -> dict:
        if page_token is None:
            url = "https://esports-api.lolesports.com/persisted/gw/getSchedule?hl=en-GB"
        else:
            url = (
                "https://esports-api.lolesports.com/persisted/gw/getSchedule?hl=en-GB"
                f"&pageToken={page_token}"
            )
        response = self.make_request(url)
        if response.status_code != HTTPStatus.OK:
            raise RiotApiStatusCodeAssertException(HTTPStatus.OK, response.status_code, url)

        res_json = response.json()
        return res_json["data"].get("schedule", {})


def parse_team_metadata(team_metadata: dict, game_id: str) \
        -> List[schemas.PlayerGameMetadataSchema]:
    participant_metadata = team_metadata.get("participantMetadata", [])
    player_metadata_for_team = []
    for participant in participant_metadata:
        new_player_metadata = schemas.PlayerGameMetadataSchema()
        new_player_metadata.game_id = game_id
        new_player_metadata.participant_id = participant['participantId']
        new_player_metadata.champion_id = participant['championId']
        new_player_metadata.role = participant['role']
        # Weird edge case where it doesn't exist for some games:
        new_player_metadata.player_id = participant.get(
            'esportsPlayerId', str(new_player_metadata.participant_id))
        player_metadata_for_team.append(new_player_metadata)
    return player_metadata_for_team
