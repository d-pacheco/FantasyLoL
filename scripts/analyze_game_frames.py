"""Analyze a game frames JSON for duration, multi-kills, and dragon tracking."""

import argparse
import json
from datetime import datetime


def parse_ts(ts: str) -> datetime:
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(ts, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse timestamp: {ts}")


def find_game_start_idx(frames: list[dict]) -> int:
    """Game starts when gold first appears (players leave fountain)."""
    for i, f in enumerate(frames):
        if f["blueTeam"]["totalGold"] > 0 or f["redTeam"]["totalGold"] > 0:
            return i
    return 0


def calculate_duration(frames: list[dict], start_idx: int) -> dict:
    """Calculate game duration, subtracting pause time."""
    start_ts = parse_ts(frames[start_idx]["rfc460Timestamp"])
    end_ts = parse_ts(frames[-1]["rfc460Timestamp"])

    # Find all pause windows
    pauses = []
    pause_start = None
    for f in frames[start_idx:]:
        if f["gameState"] == "paused" and pause_start is None:
            pause_start = parse_ts(f["rfc460Timestamp"])
        elif f["gameState"] != "paused" and pause_start is not None:
            pauses.append((pause_start, parse_ts(f["rfc460Timestamp"])))
            pause_start = None

    total_pause_seconds = sum((end - start).total_seconds() for start, end in pauses)
    raw_seconds = (end_ts - start_ts).total_seconds()
    effective_seconds = raw_seconds - total_pause_seconds

    return {
        "raw_duration": int(raw_seconds),
        "pause_count": len(pauses),
        "total_pause_seconds": int(total_pause_seconds),
        "effective_duration_seconds": int(effective_seconds),
        "effective_duration_formatted": f"{int(effective_seconds)//60}:{int(effective_seconds)%60:02d}",
        "pauses": [
            {
                "start": start.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "end": end.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "duration_seconds": int((end - start).total_seconds()),
            }
            for start, end in pauses
        ],
    }


def detect_multi_kills(frames: list[dict], start_idx: int, metadata: dict) -> list[dict]:
    """
    Detect multi-kills by tracking per-player kill increments and checking
    if multiple kills happen within 10s (30s window after quadra for penta).
    A penta window ends early if any enemy respawns.
    """
    # Build participant info lookup
    participants = {}
    for p in metadata["blueTeamMetadata"]["participantMetadata"]:
        participants[p["participantId"]] = {"name": p["summonerName"], "champion": p["championId"], "team": "blue"}
    for p in metadata["redTeamMetadata"]["participantMetadata"]:
        participants[p["participantId"]] = {"name": p["summonerName"], "champion": p["championId"], "team": "red"}

    # Collect kill events (timestamp when a player's kill count increments)
    kill_events = []  # (timestamp_dt, killer_id)
    prev_kills = {}
    for f in frames[start_idx:]:
        if f["gameState"] == "paused":
            continue
        ts = parse_ts(f["rfc460Timestamp"])
        for team_key in ["blueTeam", "redTeam"]:
            for p in f[team_key]["participants"]:
                pid = p["participantId"]
                if pid not in prev_kills:
                    prev_kills[pid] = p["kills"]
                    continue
                if p["kills"] > prev_kills[pid]:
                    for _ in range(p["kills"] - prev_kills[pid]):
                        kill_events.append((ts, pid))
                    prev_kills[pid] = p["kills"]

    # Collect respawn events (enemy health goes 0 -> positive)
    respawn_events = []  # (timestamp_dt, player_id)
    prev_health = {}
    for f in frames[start_idx:]:
        if f["gameState"] == "paused":
            continue
        ts = parse_ts(f["rfc460Timestamp"])
        for team_key in ["blueTeam", "redTeam"]:
            for p in f[team_key]["participants"]:
                pid = p["participantId"]
                if pid not in prev_health:
                    prev_health[pid] = p["currentHealth"]
                    continue
                if prev_health[pid] == 0 and p["currentHealth"] > 0:
                    respawn_events.append((ts, pid))
                prev_health[pid] = p["currentHealth"]

    def enemy_respawned_between(killer_id: int, after: datetime, before: datetime) -> bool:
        """Check if any enemy of the killer respawned in the time window."""
        killer_team = participants[killer_id]["team"]
        for resp_ts, resp_pid in respawn_events:
            if resp_ts <= after or resp_ts > before:
                continue
            resp_team = participants[resp_pid]["team"]
            if resp_team != killer_team:
                return True
        return False

    # Group consecutive kills by the same player and check time windows
    multi_kills = []
    i = 0
    while i < len(kill_events):
        ts, killer_id = kill_events[i]
        streak = [(ts, killer_id)]
        j = i + 1

        while j < len(kill_events):
            next_ts, next_killer = kill_events[j]
            if next_killer != killer_id:
                j += 1
                continue

            last_kill_ts = streak[-1][0]
            window = 30 if len(streak) == 4 else 10
            elapsed = (next_ts - last_kill_ts).total_seconds()

            if elapsed > window:
                break

            # For penta window: check if enemy respawned
            if len(streak) == 4 and enemy_respawned_between(killer_id, last_kill_ts, next_ts):
                break

            streak.append((next_ts, next_killer))
            j += 1

        if len(streak) >= 2:
            names = {2: "Double Kill", 3: "Triple Kill", 4: "Quadra Kill", 5: "Penta Kill"}
            multi_kills.append({
                "type": names.get(len(streak), f"{len(streak)}-kill"),
                "player": participants[killer_id]["name"],
                "champion": participants[killer_id]["champion"],
                "team": participants[killer_id]["team"],
                "kill_count": len(streak),
                "start_time": streak[0][0].strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "end_time": streak[-1][0].strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "window_seconds": round((streak[-1][0] - streak[0][0]).total_seconds(), 1),
            })
            # Skip past the kills we already counted for this player
            i = j
        else:
            i += 1

    return multi_kills


def track_dragons(frames: list[dict], start_idx: int) -> dict:
    """Track dragon kills in order, noting which team took each one."""
    dragon_events = []
    last_blue = []
    last_red = []

    for f in frames[start_idx:]:
        bd = f["blueTeam"]["dragons"]
        rd = f["redTeam"]["dragons"]
        if bd != last_blue:
            dragon_events.append({
                "order": len(dragon_events) + 1,
                "team": "blue",
                "dragon_type": bd[-1],
                "timestamp": f["rfc460Timestamp"],
                "team_dragon_count": len(bd),
            })
            last_blue = bd
        if rd != last_red:
            dragon_events.append({
                "order": len(dragon_events) + 1,
                "team": "red",
                "dragon_type": rd[-1],
                "timestamp": f["rfc460Timestamp"],
                "team_dragon_count": len(rd),
            })
            last_red = rd

    # Determine dragon soul (4th dragon for a team)
    soul = None
    for e in dragon_events:
        if e["team_dragon_count"] == 4:
            soul = {"team": e["team"], "dragon_type": e["dragon_type"]}
            break

    return {
        "total_dragons": len(dragon_events),
        "first_dragon": dragon_events[0] if dragon_events else None,
        "dragon_soul": soul,
        "events": dragon_events,
    }


def main():
    parser = argparse.ArgumentParser(description="Analyze game frames JSON")
    parser.add_argument("file", help="Path to frames JSON file")
    args = parser.parse_args()

    with open(args.file) as f:
        data = json.load(f)

    frames = data["frames"]
    metadata = data["gameMetadata"]
    start_idx = find_game_start_idx(frames)

    print(f"=== Game Analysis: {data['esportsGameId']} ===\n")

    # 1. Duration
    duration = calculate_duration(frames, start_idx)
    print(f"GAME DURATION: {duration['effective_duration_formatted']}")
    print(f"  Raw duration: {duration['raw_duration']//60}:{duration['raw_duration']%60:02d}")
    print(f"  Pauses: {duration['pause_count']}")
    for p in duration["pauses"]:
        print(f"    - {p['duration_seconds']}s pause ({p['start']} -> {p['end']})")
    print()

    # 2. Multi-kills
    multi_kills = detect_multi_kills(frames, start_idx, metadata)
    print(f"MULTI-KILLS: {len(multi_kills)} detected")
    for mk in multi_kills:
        print(f"  {mk['type']} - {mk['player']} ({mk['champion']}, {mk['team']}) "
              f"over {mk['window_seconds']}s")
    print()

    # 3. Dragons
    dragons = track_dragons(frames, start_idx)
    print(f"DRAGONS: {dragons['total_dragons']} total")
    if dragons["first_dragon"]:
        fd = dragons["first_dragon"]
        print(f"  First dragon: {fd['dragon_type']} taken by {fd['team']}")
    if dragons["dragon_soul"]:
        ds = dragons["dragon_soul"]
        print(f"  Dragon Soul: {ds['dragon_type']} ({ds['team']} team)")
    print("  Order:")
    for e in dragons["events"]:
        print(f"    {e['order']}. {e['dragon_type']} - {e['team']} (team total: {e['team_dragon_count']})")


if __name__ == "__main__":
    main()
