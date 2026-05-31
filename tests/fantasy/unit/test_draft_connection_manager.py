import asyncio
from unittest.mock import AsyncMock

from tests.test_base import TestBase
from src.common.schemas.fantasy_schemas import (
    DraftCompletedEvent,
    FantasyLeagueID,
)


class TestDraftConnectionManager(TestBase):
    def setUp(self):
        super().setUp()
        from src.fantasy.service.draft_connection_manager import DraftConnectionManager

        self.manager = DraftConnectionManager()
        self.league_id = FantasyLeagueID("test-league")

    def make_ws(self):
        ws = AsyncMock()
        return ws

    # --------------------------------------------------
    # ------------------- connect ----------------------
    # --------------------------------------------------
    def test_connect_adds_websocket_to_room(self):
        # Arrange
        ws = self.make_ws()

        # Act
        self.manager.connect(self.league_id, ws)

        # Assert
        self.assertIn(ws, self.manager.get_connections(self.league_id))

    # --------------------------------------------------
    # ------------------ disconnect --------------------
    # --------------------------------------------------
    def test_disconnect_removes_websocket_from_room(self):
        # Arrange
        ws = self.make_ws()
        self.manager.connect(self.league_id, ws)

        # Act
        self.manager.disconnect(self.league_id, ws)

        # Assert
        self.assertNotIn(ws, self.manager.get_connections(self.league_id))

    def test_disconnect_nonexistent_connection_does_nothing(self):
        # Arrange
        ws = self.make_ws()

        # Act & Assert — no error
        self.manager.disconnect(self.league_id, ws)

    # --------------------------------------------------
    # ------------------- broadcast --------------------
    # --------------------------------------------------
    def test_broadcast_sends_message_to_all_connections(self):
        # Arrange
        ws1 = self.make_ws()
        ws2 = self.make_ws()
        self.manager.connect(self.league_id, ws1)
        self.manager.connect(self.league_id, ws2)
        event = DraftCompletedEvent()

        # Act
        asyncio.run(self.manager.broadcast(self.league_id, event))

        # Assert
        expected = event.model_dump_json()
        ws1.send_text.assert_called_once_with(expected)
        ws2.send_text.assert_called_once_with(expected)

    def test_broadcast_to_empty_room_does_nothing(self):
        # Act & Assert — no error
        asyncio.run(self.manager.broadcast(self.league_id, DraftCompletedEvent()))

    # --------------------------------------------------
    # ------------------ close_room --------------------
    # --------------------------------------------------
    def test_close_room_closes_all_connections_and_removes_room(self):
        # Arrange
        ws1 = self.make_ws()
        ws2 = self.make_ws()
        self.manager.connect(self.league_id, ws1)
        self.manager.connect(self.league_id, ws2)

        # Act
        asyncio.run(self.manager.close_room(self.league_id))

        # Assert
        ws1.close.assert_called_once()
        ws2.close.assert_called_once()
        self.assertEqual([], self.manager.get_connections(self.league_id))

    def test_close_room_nonexistent_room_does_nothing(self):
        # Act & Assert — no error
        asyncio.run(self.manager.close_room(self.league_id))
