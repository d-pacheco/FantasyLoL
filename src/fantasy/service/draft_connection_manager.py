from fastapi import WebSocket

from src.common.schemas.fantasy_schemas import FantasyLeagueID


class DraftConnectionManager:
    def __init__(self):
        self._rooms: dict[str, set[WebSocket]] = {}

    def connect(self, league_id: FantasyLeagueID, websocket: WebSocket) -> None:
        if league_id not in self._rooms:
            self._rooms[league_id] = set()
        self._rooms[league_id].add(websocket)

    def disconnect(self, league_id: FantasyLeagueID, websocket: WebSocket) -> None:
        if league_id in self._rooms:
            self._rooms[league_id].discard(websocket)

    def get_connections(self, league_id: FantasyLeagueID) -> list[WebSocket]:
        return list(self._rooms.get(league_id, set()))

    async def broadcast(self, league_id: FantasyLeagueID, message: str) -> None:
        for ws in list(self._rooms.get(league_id, set())):
            await ws.send_text(message)

    async def close_room(self, league_id: FantasyLeagueID) -> None:
        for ws in list(self._rooms.get(league_id, set())):
            await ws.close()
        self._rooms.pop(league_id, None)
