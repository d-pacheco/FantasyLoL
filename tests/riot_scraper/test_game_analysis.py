from src.riot_scraper.game_analysis import detect_multi_kills, MultiKill
from src.riot_scraper.riot_api.schemas.get_live_window import (
    WindowFrame,
    TeamWindowFrame,
    ParticipantWindowFrame,
)
from src.common.schemas.riot_data_schemas import LiveGameState


def _make_participant(participant_id, kills=0, current_health=100):
    return ParticipantWindowFrame(
        participantId=participant_id,
        totalGold=0,
        level=1,
        kills=kills,
        deaths=0,
        assists=0,
        creepScore=0,
        currentHealth=current_health,
        maxHealth=100,
    )


def _make_frame(timestamp, blue_participants, red_participants=None):
    if red_participants is None:
        red_participants = [
            _make_participant(6),
            _make_participant(7),
            _make_participant(8),
            _make_participant(9),
            _make_participant(10),
        ]
    return WindowFrame(
        rfc460Timestamp=timestamp,
        gameState=LiveGameState.IN_GAME,
        blueTeam=TeamWindowFrame(
            totalGold=0,
            inhibitors=0,
            towers=0,
            barons=0,
            totalKills=0,
            dragons=[],
            participants=blue_participants,
        ),
        redTeam=TeamWindowFrame(
            totalGold=0,
            inhibitors=0,
            towers=0,
            barons=0,
            totalKills=0,
            dragons=[],
            participants=red_participants,
        ),
    )


class TestDetectMultiKills:
    def test_double_kill_within_10_seconds(self):
        frames = [
            _make_frame("2024-01-01T00:00:00.000Z", [_make_participant(1, kills=0)]),
            _make_frame("2024-01-01T00:00:05.000Z", [_make_participant(1, kills=1)]),
            _make_frame("2024-01-01T00:00:10.000Z", [_make_participant(1, kills=2)]),
        ]

        result = detect_multi_kills(frames)

        assert result == [MultiKill(participant_id=1, kill_number=1, kill_type="double")]

    def test_kills_outside_10_second_window_are_not_multi_kill(self):
        frames = [
            _make_frame("2024-01-01T00:00:00.000Z", [_make_participant(1, kills=0)]),
            _make_frame("2024-01-01T00:00:05.000Z", [_make_participant(1, kills=1)]),
            _make_frame("2024-01-01T00:00:16.000Z", [_make_participant(1, kills=2)]),
        ]

        result = detect_multi_kills(frames)

        assert result == []

    def test_triple_kill(self):
        frames = [
            _make_frame("2024-01-01T00:00:00.000Z", [_make_participant(1, kills=0)]),
            _make_frame("2024-01-01T00:00:03.000Z", [_make_participant(1, kills=1)]),
            _make_frame("2024-01-01T00:00:06.000Z", [_make_participant(1, kills=2)]),
            _make_frame("2024-01-01T00:00:09.000Z", [_make_participant(1, kills=3)]),
        ]

        result = detect_multi_kills(frames)

        assert result == [MultiKill(participant_id=1, kill_number=1, kill_type="triple")]

    def test_penta_kill_uses_30_second_window_after_quadra(self):
        """After a quadra, the 5th kill has a 30s window instead of 10s."""
        frames = [
            _make_frame("2024-01-01T00:00:00.000Z", [_make_participant(1, kills=0)]),
            _make_frame("2024-01-01T00:00:03.000Z", [_make_participant(1, kills=1)]),
            _make_frame("2024-01-01T00:00:06.000Z", [_make_participant(1, kills=2)]),
            _make_frame("2024-01-01T00:00:09.000Z", [_make_participant(1, kills=3)]),
            _make_frame("2024-01-01T00:00:12.000Z", [_make_participant(1, kills=4)]),
            # 25s after 4th kill — within 30s penta window
            _make_frame("2024-01-01T00:00:37.000Z", [_make_participant(1, kills=5)]),
        ]

        result = detect_multi_kills(frames)

        assert result == [MultiKill(participant_id=1, kill_number=1, kill_type="penta")]

    def test_penta_window_exceeded_results_in_quadra(self):
        """If 5th kill is >30s after 4th, only a quadra is recorded."""
        frames = [
            _make_frame("2024-01-01T00:00:00.000Z", [_make_participant(1, kills=0)]),
            _make_frame("2024-01-01T00:00:03.000Z", [_make_participant(1, kills=1)]),
            _make_frame("2024-01-01T00:00:06.000Z", [_make_participant(1, kills=2)]),
            _make_frame("2024-01-01T00:00:09.000Z", [_make_participant(1, kills=3)]),
            _make_frame("2024-01-01T00:00:12.000Z", [_make_participant(1, kills=4)]),
            # 31s after 4th kill — outside 30s penta window
            _make_frame("2024-01-01T00:00:43.000Z", [_make_participant(1, kills=5)]),
        ]

        result = detect_multi_kills(frames)

        assert result == [MultiKill(participant_id=1, kill_number=1, kill_type="quadra")]

    def test_respawn_cutoff_ends_penta_window(self):
        """If an enemy respawns after quadra, penta window ends even if within 30s."""
        frames = [
            _make_frame(
                "2024-01-01T00:00:00.000Z",
                [_make_participant(1, kills=0)],
                [
                    _make_participant(6, current_health=100),
                    _make_participant(7),
                    _make_participant(8),
                    _make_participant(9),
                    _make_participant(10),
                ],
            ),
            _make_frame(
                "2024-01-01T00:00:03.000Z",
                [_make_participant(1, kills=1)],
                [
                    _make_participant(6, current_health=0),
                    _make_participant(7),
                    _make_participant(8),
                    _make_participant(9),
                    _make_participant(10),
                ],
            ),
            _make_frame(
                "2024-01-01T00:00:06.000Z",
                [_make_participant(1, kills=2)],
                [
                    _make_participant(6, current_health=0),
                    _make_participant(7),
                    _make_participant(8),
                    _make_participant(9),
                    _make_participant(10),
                ],
            ),
            _make_frame(
                "2024-01-01T00:00:09.000Z",
                [_make_participant(1, kills=3)],
                [
                    _make_participant(6, current_health=0),
                    _make_participant(7),
                    _make_participant(8),
                    _make_participant(9),
                    _make_participant(10),
                ],
            ),
            _make_frame(
                "2024-01-01T00:00:12.000Z",
                [_make_participant(1, kills=4)],
                [
                    _make_participant(6, current_health=0),
                    _make_participant(7),
                    _make_participant(8),
                    _make_participant(9),
                    _make_participant(10),
                ],
            ),
            # Enemy respawns
            _make_frame(
                "2024-01-01T00:00:15.000Z",
                [_make_participant(1, kills=4)],
                [
                    _make_participant(6, current_health=100),
                    _make_participant(7),
                    _make_participant(8),
                    _make_participant(9),
                    _make_participant(10),
                ],
            ),
            # 5th kill within 30s but after respawn — should NOT count as penta
            _make_frame(
                "2024-01-01T00:00:20.000Z",
                [_make_participant(1, kills=5)],
                [
                    _make_participant(6, current_health=100),
                    _make_participant(7),
                    _make_participant(8),
                    _make_participant(9),
                    _make_participant(10),
                ],
            ),
        ]

        result = detect_multi_kills(frames)

        assert result == [MultiKill(participant_id=1, kill_number=1, kill_type="quadra")]

    def test_multiple_multi_kills_by_same_player(self):
        """A player gets a double kill, then later another double kill."""
        frames = [
            _make_frame("2024-01-01T00:00:00.000Z", [_make_participant(1, kills=0)]),
            _make_frame("2024-01-01T00:00:03.000Z", [_make_participant(1, kills=1)]),
            _make_frame("2024-01-01T00:00:06.000Z", [_make_participant(1, kills=2)]),
            # Gap > 10s
            _make_frame("2024-01-01T00:01:00.000Z", [_make_participant(1, kills=3)]),
            _make_frame("2024-01-01T00:01:05.000Z", [_make_participant(1, kills=4)]),
        ]

        result = detect_multi_kills(frames)

        assert result == [
            MultiKill(participant_id=1, kill_number=1, kill_type="double"),
            MultiKill(participant_id=1, kill_number=2, kill_type="double"),
        ]

    def test_interleaved_kills_by_different_players(self):
        """Two players get kills interleaved — each gets their own multi-kill."""
        frames = [
            _make_frame(
                "2024-01-01T00:00:00.000Z",
                [_make_participant(1, kills=0), _make_participant(2, kills=0)],
            ),
            _make_frame(
                "2024-01-01T00:00:03.000Z",
                [_make_participant(1, kills=1), _make_participant(2, kills=1)],
            ),
            _make_frame(
                "2024-01-01T00:00:06.000Z",
                [_make_participant(1, kills=2), _make_participant(2, kills=2)],
            ),
        ]

        result = detect_multi_kills(frames)

        assert MultiKill(participant_id=1, kill_number=1, kill_type="double") in result
        assert MultiKill(participant_id=2, kill_number=1, kill_type="double") in result
        assert len(result) == 2

    def test_kills_at_exactly_10_seconds_still_count(self):
        """Kill at exactly 10.000s after previous should still be in the window."""
        frames = [
            _make_frame("2024-01-01T00:00:00.000Z", [_make_participant(1, kills=0)]),
            _make_frame("2024-01-01T00:00:05.000Z", [_make_participant(1, kills=1)]),
            _make_frame("2024-01-01T00:00:15.000Z", [_make_participant(1, kills=2)]),
        ]

        result = detect_multi_kills(frames)

        assert result == [MultiKill(participant_id=1, kill_number=1, kill_type="double")]

    def test_other_players_kills_do_not_contribute_to_streak(self):
        """Player 2 getting kills between player 1's kills doesn't extend player 1's window."""
        frames = [
            _make_frame(
                "2024-01-01T00:00:00.000Z",
                [_make_participant(1, kills=0), _make_participant(2, kills=0)],
            ),
            _make_frame(
                "2024-01-01T00:00:03.000Z",
                [_make_participant(1, kills=1), _make_participant(2, kills=0)],
            ),
            # Player 2 gets a kill — should NOT help player 1's streak
            _make_frame(
                "2024-01-01T00:00:08.000Z",
                [_make_participant(1, kills=1), _make_participant(2, kills=1)],
            ),
            # Player 1's second kill is >10s after their first — no multi-kill
            _make_frame(
                "2024-01-01T00:00:14.000Z",
                [_make_participant(1, kills=2), _make_participant(2, kills=1)],
            ),
        ]

        result = detect_multi_kills(frames)

        # Player 1: kills at 3s and 14s — 11s apart, no multi-kill
        # Player 2: only 1 kill total, no multi-kill
        assert result == []

    def test_only_own_kills_count_toward_streak(self):
        """A player's streak is based solely on their own kill timestamps."""
        frames = [
            _make_frame(
                "2024-01-01T00:00:00.000Z",
                [_make_participant(1, kills=0), _make_participant(2, kills=0)],
            ),
            _make_frame(
                "2024-01-01T00:00:03.000Z",
                [_make_participant(1, kills=1), _make_participant(2, kills=1)],
            ),
            _make_frame(
                "2024-01-01T00:00:06.000Z",
                [_make_participant(1, kills=1), _make_participant(2, kills=2)],
            ),
            _make_frame(
                "2024-01-01T00:00:09.000Z",
                [_make_participant(1, kills=1), _make_participant(2, kills=3)],
            ),
        ]

        result = detect_multi_kills(frames)

        # Player 1: only 1 kill, no multi-kill
        # Player 2: 3 kills within 6s = triple
        assert result == [MultiKill(participant_id=2, kill_number=1, kill_type="triple")]


from src.riot_scraper.game_analysis import detect_dragon_order, DragonKill


class TestDetectDragonOrder:
    def test_dragons_alternating_between_teams(self):
        """Dragons taken by alternating teams are stored in chronological order."""
        frames = [
            _make_frame("2024-01-01T00:00:00.000Z", [_make_participant(1)]),
            _make_frame("2024-01-01T00:05:00.000Z", [_make_participant(1)]),
            _make_frame("2024-01-01T00:10:00.000Z", [_make_participant(1)]),
            _make_frame("2024-01-01T00:15:00.000Z", [_make_participant(1)]),
        ]
        # Frame 0: no dragons
        # Frame 1: blue gets infernal
        frames[1].blueTeam.dragons = ["infernal"]
        # Frame 2: red gets mountain (blue still has infernal)
        frames[2].blueTeam.dragons = ["infernal"]
        frames[2].redTeam.dragons = ["mountain"]
        # Frame 3: blue gets ocean
        frames[3].blueTeam.dragons = ["infernal", "ocean"]
        frames[3].redTeam.dragons = ["mountain"]

        result = detect_dragon_order(frames, "blue-team-id", "red-team-id")

        assert result == [
            DragonKill(dragon_number=1, team_id="blue-team-id", dragon_type="infernal"),
            DragonKill(dragon_number=2, team_id="red-team-id", dragon_type="mountain"),
            DragonKill(dragon_number=3, team_id="blue-team-id", dragon_type="ocean"),
        ]


from src.riot_scraper.game_analysis import compute_duration


class TestComputeDuration:
    def test_duration_with_one_pause(self):
        """Game duration subtracts a single pause period."""
        frames = [
            _make_frame("2024-01-01T00:00:00.000Z", [_make_participant(1)]),
            _make_frame("2024-01-01T00:05:00.000Z", [_make_participant(1)]),
            _make_frame("2024-01-01T00:10:00.000Z", [_make_participant(1)]),
            _make_frame("2024-01-01T00:15:00.000Z", [_make_participant(1)]),
            _make_frame("2024-01-01T00:20:00.000Z", [_make_participant(1)]),
        ]
        # Game starts at frame 0 (gold > 0)
        frames[0].blueTeam.totalGold = 500
        # Pause from frame 1 to frame 2
        frames[1].gameState = LiveGameState.PAUSED
        frames[2].gameState = LiveGameState.PAUSED
        # Game ends at frame 4
        frames[4].gameState = LiveGameState.FINISHED

        result = compute_duration(frames)

        # Total time: 20 min. Pause: frame1 (5:00) to frame3 (15:00) = 10 min.
        # Effective: 20min - 10min = 10min = 600s
        assert result == 600

    def test_duration_with_multiple_pauses(self):
        """Game duration subtracts multiple pause periods."""
        frames = [
            _make_frame("2024-01-01T00:00:00.000Z", [_make_participant(1)]),
            _make_frame("2024-01-01T00:05:00.000Z", [_make_participant(1)]),
            _make_frame("2024-01-01T00:10:00.000Z", [_make_participant(1)]),
            _make_frame("2024-01-01T00:15:00.000Z", [_make_participant(1)]),
            _make_frame("2024-01-01T00:20:00.000Z", [_make_participant(1)]),
            _make_frame("2024-01-01T00:25:00.000Z", [_make_participant(1)]),
            _make_frame("2024-01-01T00:30:00.000Z", [_make_participant(1)]),
        ]
        frames[0].blueTeam.totalGold = 500
        # First pause: frame 1 (5:00) - paused
        frames[1].gameState = LiveGameState.PAUSED
        # Resumes at frame 2 (10:00) — 5 min pause
        # Second pause: frame 4 (20:00) - paused
        frames[4].gameState = LiveGameState.PAUSED
        # Resumes at frame 5 (25:00) — 5 min pause
        # Game ends at frame 6
        frames[6].gameState = LiveGameState.FINISHED

        result = compute_duration(frames)

        # Total time: 30 min. Pauses: 5min + 5min = 10min.
        # Effective: 30min - 10min = 20min = 1200s
        assert result == 1200
