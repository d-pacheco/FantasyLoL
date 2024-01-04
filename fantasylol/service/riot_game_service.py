from typing import List

from sqlalchemy import select
from sqlalchemy.orm import aliased

from fantasylol.db.database import DatabaseConnection
from fantasylol.db.models import Game, Match
from fantasylol.util.riot_api_requester import RiotApiRequester
from fantasylol.exceptions.game_not_found_exception import GameNotFoundException


class RiotGameService:
    def __init__(self):
        self.riot_api_requester = RiotApiRequester()

    def fetch_and_store_live_games(self) -> List[Game]:
        print("Fetching and storing live games from riot's api")
        request_url = "https://esports-api.lolesports.com/persisted/gw/getLive?hl=en-GB"
        try:
            res_json = self.riot_api_requester.make_request(request_url)
            fetched_games = []
            events = res_json["data"]["schedule"].get("events", [])
            for event in events:
                if event['type'] != 'match':
                    continue
                games = event['match']['games']
                for game in games:
                    if game['state'] != 'inProgress':
                        continue
                    new_game_attrs = {
                        "id": game['id'],
                        "state": game['state'],
                        "number": game['number'],
                        "match_id": event['id']
                    }
                    new_game = Game(**new_game_attrs)
                    fetched_games.append(new_game)

            for new_game in fetched_games:
                with DatabaseConnection() as db:
                    db.merge(new_game)
                    db.commit()
            return fetched_games
        except Exception as e:
            print(f"Error: {str(e)}")
            raise e

    def fetch_and_store_games_from_match_ids(self, batch_size: int = 25):
        match_ids = self.get_matches_without_games()

        for i in range(0, len(match_ids), batch_size):
            batch = match_ids[i:i + batch_size]
            self.process_batch_match_ids(batch)

    def process_batch_match_ids(self, match_ids: List[int]):
        print("Processes batch of match ids: ", match_ids)
        fetched_games = []
        for match_id in match_ids:
            event_details_url = (
                f"https://esports-api.lolesports.com/persisted/gw/getEventDetails"
                f"?hl=en-GB&id={match_id}"
            )
            event_res_json = self.riot_api_requester.make_request(event_details_url)
            event = event_res_json['data']['event']
            games = event['match']['games']
            for game in games:
                new_game_attrs = {
                    "id": game['id'],
                    "state": game['state'],
                    "number": game['number'],
                    "match_id": event['id']
                }
                new_game = Game(**new_game_attrs)
                fetched_games.append(new_game)
        with DatabaseConnection() as db:
            db.bulk_save_objects(fetched_games)
            db.commit()

    def get_games(self, query_params: dict = None) -> List[Game]:
        with DatabaseConnection() as db:
            query = db.query(Game)

            if query_params is None:
                return query.all()

            for param_key in query_params:
                param = query_params[param_key]
                if param is None:
                    continue
                column = getattr(Game, param_key, None)
                if column is not None:
                    query = query.filter(column == param)
            games = query.all()
        return games

    def get_game_by_id(self, game_id: int) -> Game:
        with DatabaseConnection() as db:
            game = db.query(Game).filter(Game.id == game_id).first()
        if game is None:
            raise GameNotFoundException()
        return game

    @staticmethod
    def get_matches_without_games() -> List[int]:
        game_alias = aliased(Game)

        # Query to get match IDs without any associated games
        with DatabaseConnection() as db:
            subquery = (
                select([game_alias.match_id])
                .where(game_alias.match_id.isnot(None))
                .distinct()
                .alias()
            )

            # Query to get match IDs without associated games
            matches_without_games = (
                db.query(Match.id)
                .outerjoin(subquery, Match.id == subquery.c.match_id)
                .filter(subquery.c.match_id.is_(None))
                .all()
            )

        # Extract match IDs from the result
        return [match.id for match in matches_without_games]

