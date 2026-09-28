from unittest.mock import MagicMock

from src.common.schemas.riot_data_schemas import (
    Game,
    GameState,
    ProTeamID,
    RiotGameID,
    RiotMatchID,
)
from src.riot_scraper.riot_api.schemas.get_event_details import EventDetailsResponse
from src.riot_scraper.scrapers.game_scraper import RiotGameScraper
from tests.test_util import riot_fixtures

MATCH_ID = RiotMatchID("match-1")
KNOWN_TEAM = "98926509885559666"


def make_event_details(games: list[dict]) -> EventDetailsResponse:
    """Shape mirrors a real getEventDetails payload for a match with a TBD opponent."""
    return EventDetailsResponse.model_validate(
        {
            "data": {
                "event": {
                    "id": MATCH_ID,
                    "type": "match",
                    "tournament": {"id": "tournament-1"},
                    "league": {"id": "league-1", "slug": "lcs", "image": "", "name": "LCS"},
                    "match": {
                        "strategy": {"count": 5},
                        "teams": [
                            {"id": "0", "name": "TBD", "code": "TBD", "image": ""},
                            {"id": KNOWN_TEAM, "name": "TLAW", "code": "TLAW", "image": ""},
                        ],
                        "games": games,
                    },
                }
            }
        }
    )


def run_scraper(event_details: EventDetailsResponse) -> list[Game]:
    db = MagicMock()
    api = MagicMock()
    api.get_event_details.return_value = event_details
    scraper = RiotGameScraper(db, api, MagicMock())
    scraper.process_batch_match_ids([MATCH_ID])
    return db.bulk_save_games.call_args.args[0]


def test_tbd_opponent_listed_second_is_not_saved_as_team():
    # Riot lists the known team first with a side, and the TBD team ("0") with no side.
    # Previously this mapped red_team="0" and crashed on the professional_teams FK.
    response = make_event_details(
        [
            {
                "id": "game-2",
                "number": 2,
                "state": "unstarted",
                "teams": [{"id": KNOWN_TEAM, "side": "blue"}, {"id": "0", "side": None}],
            }
        ]
    )

    [game] = run_scraper(response)

    assert game.blue_team == ProTeamID(KNOWN_TEAM)
    assert game.red_team is None


def test_tbd_opponent_listed_first_keeps_known_team_side():
    response = make_event_details(
        [
            {
                "id": "game-1",
                "number": 1,
                "state": "unstarted",
                "teams": [{"id": "0", "side": None}, {"id": KNOWN_TEAM, "side": "red"}],
            }
        ]
    )

    [game] = run_scraper(response)

    assert game.red_team == ProTeamID(KNOWN_TEAM)
    assert game.blue_team is None


def test_both_teams_known_maps_sides():
    response = make_event_details(
        [
            {
                "id": "game-1",
                "number": 1,
                "state": "completed",
                "teams": [{"id": "team-a", "side": "red"}, {"id": "team-b", "side": "blue"}],
            }
        ]
    )

    [game] = run_scraper(response)

    assert game.red_team == ProTeamID("team-a")
    assert game.blue_team == ProTeamID("team-b")
    assert game.state == GameState.COMPLETED


def test_put_game_skips_team_not_in_professional_teams(db):
    db.put_league(riot_fixtures.league_1_fixture)
    db.put_team(riot_fixtures.team_1_fixture)
    db.put_tournament(riot_fixtures.tournament_fixture)
    db.put_match(riot_fixtures.match_fixture)
    game = Game(
        id=RiotGameID("game-unknown-team"),
        state=GameState.UNSTARTED,
        number=1,
        red_team=ProTeamID("0"),
        blue_team=riot_fixtures.team_1_fixture.id,
        match_id=riot_fixtures.match_fixture.id,
    )

    db.put_game(game)  # must not raise ForeignKeyViolation

    saved = db.get_game_by_id(game.id)
    assert saved is not None
    assert saved.blue_team == riot_fixtures.team_1_fixture.id
    assert saved.red_team is None


def test_tbd_game_is_refetched_until_opponent_is_known(db):
    # Real DB, real scraper: first fetch has a TBD opponent, later fetch has it resolved.
    known = riot_fixtures.team_1_fixture
    opponent = riot_fixtures.team_2_fixture
    match = riot_fixtures.match_fixture
    db.put_league(riot_fixtures.league_1_fixture)
    db.put_team(known)
    db.put_team(opponent)
    db.put_tournament(riot_fixtures.tournament_fixture)
    db.put_match(match)

    def details(red_id: str, red_side: str | None) -> EventDetailsResponse:
        response = make_event_details(
            [
                {
                    "id": "tbd-game-1",
                    "number": 1,
                    "state": "unstarted",
                    "teams": [{"id": known.id, "side": "blue"}, {"id": red_id, "side": red_side}],
                }
            ]
        )
        response.data.event.id = match.id
        return response

    api = MagicMock()
    scraper = RiotGameScraper(db, api, MagicMock())

    # Run 1: opponent undecided
    api.get_event_details.return_value = details("0", None)
    scraper.process_batch_match_ids([match.id])
    game = db.get_game_by_id(RiotGameID("tbd-game-1"))
    assert game is not None
    assert (game.blue_team, game.red_team) == (known.id, None)
    assert match.id in db.get_match_ids_without_games()

    # Run 2: Riot now knows the opponent
    api.get_event_details.return_value = details(opponent.id, "red")
    scraper.process_batch_match_ids([match.id])
    game = db.get_game_by_id(RiotGameID("tbd-game-1"))
    assert game is not None
    assert (game.blue_team, game.red_team) == (known.id, opponent.id)
    assert match.id not in db.get_match_ids_without_games()
