from dataclasses import dataclass
from datetime import timedelta

from src.common.schemas.riot_data_schemas import LiveGameState
from src.riot_scraper.riot_api.schemas.get_live_window import WindowFrame
from src.riot_scraper.timestamp_util import TimestampUtil


@dataclass(eq=True)
class MultiKill:
    participant_id: int
    kill_number: int
    kill_type: str


@dataclass(eq=True)
class DragonKill:
    dragon_number: int
    team_id: str
    dragon_type: str


MULTI_KILL_NAMES = {2: "double", 3: "triple", 4: "quadra", 5: "penta"}


def detect_multi_kills(frames: list[WindowFrame]) -> list[MultiKill]:
    """Detect multi-kills from a sequence of game frames."""
    if len(frames) < 2:
        return []

    blue_pids = {p.participantId for p in frames[0].blueTeam.participants}
    red_pids = {p.participantId for p in frames[0].redTeam.participants}
    all_pids = blue_pids | red_pids

    # Build per-frame kill counts and health for all participants
    frame_data: list[dict[int, tuple[int, int]]] = []  # pid -> (kills, currentHealth)
    for frame in frames:
        data: dict[int, tuple[int, int]] = {}
        for p in frame.blueTeam.participants + frame.redTeam.participants:
            data[p.participantId] = (p.kills, p.currentHealth)
        frame_data.append(data)

    multi_kills: list[MultiKill] = []
    kill_counters: dict[int, int] = {pid: 0 for pid in all_pids}

    for pid in all_pids:
        enemy_pids = red_pids if pid in blue_pids else blue_pids
        # Collect kill events as (frame_index, timestamp)
        kill_events: list[tuple[int, str]] = []
        for i in range(1, len(frames)):
            prev_kills = frame_data[i - 1].get(pid, (0, 0))[0]
            curr_kills = frame_data[i].get(pid, (0, 0))[0]
            new_kills = curr_kills - prev_kills
            for _ in range(new_kills):
                kill_events.append((i, frames[i].rfc460Timestamp))

        # Detect streaks
        if len(kill_events) < 2:
            continue

        streak_start = 0
        for i in range(1, len(kill_events)):
            streak_len = i - streak_start
            window = 30.0 if streak_len >= 4 else 10.0
            elapsed = _seconds_between(kill_events[i - 1][1], kill_events[i][1])

            # Check respawn cutoff: only applies when going for penta (streak_len >= 4)
            respawn_cutoff = False
            if streak_len >= 4:
                respawn_cutoff = _enemy_respawned_between(
                    frame_data,
                    enemy_pids,
                    kill_events[i - 1][0],
                    kill_events[i][0],
                )

            if elapsed > window or respawn_cutoff:
                # Record completed streak
                if streak_len >= 2:
                    kill_counters[pid] += 1
                    kill_type = MULTI_KILL_NAMES[min(streak_len, 5)]
                    multi_kills.append(
                        MultiKill(
                            participant_id=pid,
                            kill_number=kill_counters[pid],
                            kill_type=kill_type,
                        )
                    )
                streak_start = i

        # Final streak
        streak_len = len(kill_events) - streak_start
        if streak_len >= 2:
            kill_counters[pid] += 1
            kill_type = MULTI_KILL_NAMES[min(streak_len, 5)]
            multi_kills.append(
                MultiKill(
                    participant_id=pid,
                    kill_number=kill_counters[pid],
                    kill_type=kill_type,
                )
            )

    return multi_kills


def _enemy_respawned_between(
    frame_data: list[dict[int, tuple[int, int]]],
    enemy_pids: set[int],
    from_frame_idx: int,
    to_frame_idx: int,
) -> bool:
    """Check if any enemy respawned between two frame indices."""
    for fi in range(from_frame_idx, to_frame_idx + 1):
        if fi == 0:
            continue
        for epid in enemy_pids:
            prev_health = frame_data[fi - 1].get(epid, (0, 0))[1]
            curr_health = frame_data[fi].get(epid, (0, 0))[1]
            if prev_health == 0 and curr_health > 0:
                return True
    return False


def _seconds_between(ts1: str, ts2: str) -> float:
    dt1 = TimestampUtil.parse_rfc3339(ts1)
    dt2 = TimestampUtil.parse_rfc3339(ts2)
    return abs((dt2 - dt1).total_seconds())


def detect_dragon_order(
    frames: list[WindowFrame], blue_team_id: str, red_team_id: str
) -> list[DragonKill]:
    """Detect chronological dragon order by diffing team dragon lists frame-by-frame."""
    results: list[DragonKill] = []
    prev_blue: list[str] = []
    prev_red: list[str] = []

    for frame in frames:
        curr_blue = frame.blueTeam.dragons
        curr_red = frame.redTeam.dragons

        for dragon_type in curr_blue[len(prev_blue) :]:
            results.append(
                DragonKill(
                    dragon_number=len(results) + 1,
                    team_id=blue_team_id,
                    dragon_type=dragon_type,
                )
            )

        for dragon_type in curr_red[len(prev_red) :]:
            results.append(
                DragonKill(
                    dragon_number=len(results) + 1,
                    team_id=red_team_id,
                    dragon_type=dragon_type,
                )
            )

        prev_blue = curr_blue
        prev_red = curr_red

    return results


def compute_duration(frames: list[WindowFrame]) -> int:
    """Compute effective game duration in seconds, subtracting pauses.

    Finds the game start (first frame where any team has gold > 0),
    the game end (first FINISHED frame), and subtracts all pause durations.
    """
    start_time = None
    end_time = None
    paused_timestamp = None
    pauses: list[tuple[str, str]] = []

    for frame in frames:
        if start_time is None:
            if frame.blueTeam.totalGold != 0 or frame.redTeam.totalGold != 0:
                start_time = frame.rfc460Timestamp

        if frame.gameState == LiveGameState.PAUSED:
            if paused_timestamp is None:
                paused_timestamp = frame.rfc460Timestamp
        else:
            if paused_timestamp is not None:
                pauses.append((paused_timestamp, frame.rfc460Timestamp))
                paused_timestamp = None

        if frame.gameState == LiveGameState.FINISHED:
            end_time = frame.rfc460Timestamp
            break

    if start_time is None or end_time is None:
        return 0

    start_dt = TimestampUtil.parse_rfc3339(start_time)
    end_dt = TimestampUtil.parse_rfc3339(end_time)

    total_pause = timedelta()
    for pause_start, pause_end in pauses:
        total_pause += TimestampUtil.parse_rfc3339(pause_end) - TimestampUtil.parse_rfc3339(
            pause_start
        )

    effective = end_dt - start_dt - total_pause
    return int(effective.total_seconds())
