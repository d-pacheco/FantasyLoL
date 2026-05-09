"""Fetch all frames of a game from Riot's esports feed API and dump to JSON."""

import argparse
import json
import sys
from datetime import datetime, timedelta

import cloudscraper
import certifi


FEED_URL = "https://feed.lolesports.com/livestats/v1"
HEADERS = {
    "Origin": "https://lolesports.com",
    "Referrer": "https://lolesports.com",
    "x-api-key": "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z",
}


def make_request(client, url):
    response = client.get(url, headers=HEADERS, verify=certifi.where())
    if response.status_code == 204:
        return None
    if response.status_code != 200:
        print(f"Error: {response.status_code} for {url}", file=sys.stderr)
        return None
    return response.json()


def round_to_10_seconds(timestamp: str) -> str:
    dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    rounded_seconds = round(dt.second / 10) * 10
    return dt.replace(second=rounded_seconds, microsecond=0).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def add_10_seconds(timestamp: str) -> str:
    dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    dt += timedelta(seconds=10)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def fetch_all_frames(game_id: str) -> dict:
    client = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "desktop": True}
    )

    # Get initial window to find start time
    initial = make_request(client, f"{FEED_URL}/window/{game_id}?hl=en-GB")
    if not initial:
        print("Failed to fetch initial window", file=sys.stderr)
        sys.exit(1)

    metadata = initial.get("gameMetadata")
    all_frames = []
    seen_timestamps = set()

    # Start from the first frame's timestamp
    start_ts = round_to_10_seconds(initial["frames"][0]["rfc460Timestamp"])
    current_ts = start_ts
    game_finished = False

    print(f"Fetching frames for game {game_id}...")

    while not game_finished:
        window = make_request(
            client, f"{FEED_URL}/window/{game_id}?hl=en-GB&startingTime={current_ts}"
        )
        if not window:
            break

        for frame in window["frames"]:
            ts = frame["rfc460Timestamp"]
            if ts not in seen_timestamps:
                seen_timestamps.add(ts)
                all_frames.append(frame)
            if frame["gameState"] == "finished":
                game_finished = True

        current_ts = add_10_seconds(current_ts)

    print(f"Collected {len(all_frames)} frames")

    return {
        "esportsGameId": initial.get("esportsGameId"),
        "esportsMatchId": initial.get("esportsMatchId"),
        "gameMetadata": metadata,
        "frames": all_frames,
    }


def main():
    parser = argparse.ArgumentParser(description="Dump all frames of a game to JSON")
    parser.add_argument("game_id", help="Riot esports game ID")
    parser.add_argument(
        "-o", "--output", default=None, help="Output file (default: {game_id}_frames.json)"
    )
    args = parser.parse_args()

    output_file = args.output or f"{args.game_id}_frames.json"
    result = fetch_all_frames(args.game_id)

    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
