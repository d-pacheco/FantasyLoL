from unittest.mock import MagicMock


from src.common.schemas.riot_data_schemas import RiotGameID, ProTeamID
from src.riot_scraper.scrapers.game_stats_scraper import RiotGameStatsScraper
from src.riot_scraper.riot_api.schemas.get_live_window import (
    GetLiveWindowResponse,
    GameMetaData,
    TeamMetaData,
    WindowFrame,
    TeamWindowFrame,
)
from src.common.schemas.riot_data_schemas import LiveGameState


def make_window_response(
    blue_team_id: str = "blue-team-id",
    red_team_id: str = "red-team-id",
    blue_towers: int = 8,
    blue_barons: int = 1,
    blue_inhibitors: int = 2,
    blue_kills: int = 15,
    red_towers: int = 5,
    red_barons: int = 0,
    red_inhibitors: int = 1,
    red_kills: int = 10,
) -> GetLiveWindowResponse:
    return GetLiveWindowResponse(
        esportsGameId=RiotGameID("game-1"),
        esportsMatchId="match-1",
        gameMetadata=GameMetaData(
            patchVersion="14.1",
            blueTeamMetadata=TeamMetaData(
                esportsTeamId=ProTeamID(blue_team_id),
                participantMetadata=[],
            ),
            redTeamMetadata=TeamMetaData(
                esportsTeamId=ProTeamID(red_team_id),
                participantMetadata=[],
            ),
        ),
        frames=[
            WindowFrame(
                rfc460Timestamp="2026-01-01T00:30:00Z",
                gameState=LiveGameState.IN_GAME,
                blueTeam=TeamWindowFrame(
                    totalGold=50000,
                    inhibitors=blue_inhibitors,
                    towers=blue_towers,
                    barons=blue_barons,
                    totalKills=blue_kills,
                    dragons=["infernal", "mountain"],
                    participants=[],
                ),
                redTeam=TeamWindowFrame(
                    totalGold=45000,
                    inhibitors=red_inhibitors,
                    towers=red_towers,
                    barons=red_barons,
                    totalKills=red_kills,
                    dragons=["ocean"],
                    participants=[],
                ),
            ),
        ],
    )


class TestGameStatsScraperTeamStats:
    def test_fetches_both_blue_and_red_team_stats(self):
        """Both blue and red team stats should be stored with correct team IDs."""
        mock_db = MagicMock()
        mock_api = MagicMock()
        mock_job_runner = MagicMock()

        scraper = RiotGameStatsScraper(mock_db, mock_api, mock_job_runner)

        # Mock the API responses
        mock_api.get_game_details.return_value = MagicMock(frames=[MagicMock(participants=[])])
        mock_api.get_game_window.return_value = make_window_response(
            blue_team_id="team-t1",
            red_team_id="team-geng",
            blue_towers=9,
            blue_barons=2,
            blue_inhibitors=3,
            blue_kills=20,
            red_towers=5,
            red_barons=0,
            red_inhibitors=1,
            red_kills=12,
        )

        scraper.fetch_and_store_player_stats_for_game(RiotGameID("game-1"), False)

        # Check put_team_stats was called twice (once per team)
        team_stats_calls = mock_db.put_team_stats.call_args_list
        assert len(team_stats_calls) == 2

        # First call: blue team
        blue_stats = team_stats_calls[0][0][0]
        assert blue_stats.team_id == ProTeamID("team-t1")
        assert blue_stats.towers == 9
        assert blue_stats.barons == 2
        assert blue_stats.inhibitors == 3
        assert blue_stats.total_kills == 20

        # Second call: red team
        red_stats = team_stats_calls[1][0][0]
        assert red_stats.team_id == ProTeamID("team-geng")
        assert red_stats.towers == 5
        assert red_stats.barons == 0
        assert red_stats.inhibitors == 1
        assert red_stats.total_kills == 12
