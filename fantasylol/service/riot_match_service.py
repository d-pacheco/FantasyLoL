from typing import List
from fantasylol.db.database import DatabaseConnection
from fantasylol.db.models import Match
from fantasylol.exceptions.match_not_found_exception import MatchNotFoundException
from fantasylol.util.riot_api_requester import RiotApiRequester

class RiotMatchService:
    def __init__(self):
        self.riot_api_requester = RiotApiRequester()

    def fetch_and_store_matchs_from_tournament(
            self, tournament_id: int) -> List[Match]:
        print(f"Fetching matches for tournament with id {tournament_id}")
        request_url = (
            "https://esports-api.lolesports.com/persisted/gw"
            f"/getCompletedEvents?hl=en-GB&tournamentId={tournament_id}"
        )
        try:
            res_json = self.riot_api_requester.make_request(request_url)
            fetched_matches = []
            events = res_json["data"]["schedule"].get("events", [])
            for event in events:
                match = event['match']
                new_match_attrs = {
                    "id": int(match['id']),
                    "start_time": event['startTime'],
                    "block_name": event['blockName'],
                    "league_name": event['league']['name'],
                    "strategy_type": match['strategy']['type'],
                    "strategy_count": match['strategy']['count'],
                    "tournament_id": int(tournament_id),
                    "team_1_name": match['teams'][0]['name'],
                    "team_2_name": match['teams'][1]['name']
                }
                new_match = Match(**new_match_attrs)
                fetched_matches.append(new_match)
            
            print("Saving fetched matches to db")
            for new_match in fetched_matches:
                with DatabaseConnection() as db:
                    db.merge(new_match)
                    db.commit()
            return fetched_matches
        except Exception as e:
            print(f"Error: {str(e)}")
            raise e
        
    def get_matches(self, query_params: dict = None) -> List[Match]:
        with DatabaseConnection() as db:
            query = db.query(Match)

            if query_params is None:
                return query.all()
            
            for param_key in query_params:
                param = query_params[param_key]
                if param is None:
                    continue
                column = getattr(Match, param_key, None)
                if column is not None:
                    query = query.filter(column == param)
            matches = query.all()
        return matches
        
    def get_match_by_id(self, match_id: int) -> Match:
        with DatabaseConnection() as db:
            match = db.query(Match).filter(Match.id == match_id).first()
        if match is None:
            raise MatchNotFoundException()
        return match
